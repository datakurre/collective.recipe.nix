# -*- coding: utf-8 -*-
import hashlib
import os
import urllib
import re
import zc.recipe.egg
import zc.buildout.easy_install

from pkg_resources import Requirement


# Map requirements to nixpkgs
NIXPKGS = {
    'lxml': 'pythonPackages.lxml',
    'Pillow': 'pythonPackages.pillow',
    'python-ldap': 'pythonPackages.ldap'
}

# Some packages require additional build input
BUILD_INPUTS = {
    'Products.DCWorkflow': ['eggtestinfo'],
    'Products.CMFUid': ['eggtestinfo'],
    'Products.CMFActionIcons': ['eggtestinfo'],
    'dataflake.fakeldap': ['pythonPackages."setuptools-git"'],
    'Products.LDAPUserFolder': ['pythonPackages."setuptools-git"']
}

# Some packages may be available only from outside PyPI
URLS = {
}

# And some of those required build inputs are not yet available at nixpkgs
EXPRESSIONS = {
    'eggtestinfo': """\
  eggtestinfo = buildPythonPackage {
    name = "eggtestinfo-0.3";
    src = fetchurl {
        url = "https://pypi.python.org/packages/source/e/eggtestinfo/eggtestinfo-0.3.tar.gz";
        md5 = "6f0507aee05f00c640c0d64b5073f840";
    };
    doCheck = false;
  };
"""
}

# Filter buildout supported source distributions from eggs and wheels
SDIST_URL = re.compile('.*tar.gz$|.*zip$')


def prefix(s, prefix='_'):
    return prefix + s


def normalize(s):
    # Normalize given derivation name and prefix it with '_' to avoid
    # possible nixpkgs conflicts
    return re.sub('[\.\-\s\[]', '_', s)


def listify(s):
    return filter(bool, map(str.strip, (s or '').split()))


def see(project_name, requirements, ws, seen):
    for req in requirements:
        key = '{0:s}-{1:s}'.format(*sorted([
            normalize(project_name), normalize(req.project_name)]))
        if key not in seen:
            seen[key] = True
            see(project_name, ws.find(req).requires(req.extras), ws, seen)


def resolve_dependencies(requirements, ws, inject, requires=None, seen=None):

    # Init
    if seen is None:
        seen = {}
    if requires is None:
        requires = {}

    # Resolve
    for requirement in requirements:
        distribution = ws.find(requirement)
        name = distribution.project_name

        if name in requires:
            continue

        requires[name] = []

        distribution_requires = distribution.requires(requirement.extras)
        distribution_requires += inject.get(normalize(name), [])

        for req in [normalize(ws.find(r).project_name)
                    for r in distribution_requires]:
            key = '{0:s}-{1:s}'.format(*sorted([normalize(name), req]))
            if key not in seen and req not in requires[name]:
                requires[name].append(req)

        see(name, distribution_requires, ws, seen)
        resolve_dependencies(distribution_requires, ws, inject, requires, seen)

    return requires


def spliturl(url):
    if '#md5=' in url:
        return url.split('#md5=', 1)
    elif '#' in url:
        return url.split('#', 1)
    return url, ''


class Nix(object):

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.options = options

        # Set allowed outputs
        self.outputs = listify(options.get('outputs', '') or '')

        # Set allow cached flag
        self.allow_from_cache = (
            options.get('allow-from-cache', '').strip().lower()
            in ('true', 'yes', 'on', 'enable', 'enabled', '1')
        )

        # Set filename prefix
        self.prefix = os.path.join(
            (options.get('prefix') or '').strip(),
            (options.get('name') or '').strip() or name)

        # Parse propagatedBuildInputs from buildout already in __init__ to pass
        # found additional eggs forward to zc.recipe.egg
        propagated_eggs = []
        propagated_build_inputs = {}
        for section in listify(self.options.get('propagated-build-inputs')):
            if section in self.buildout:
                for key, value in self.buildout.get(section).items():
                    propagated_build_inputs[key] = listify(value)
                    propagated_eggs.extend(listify(value))
            elif '=' in section:
                # is not a section, but inline mapping
                key, value = section.split('=', 1)
                propagated_build_inputs.setdefault(key, [])
                propagated_build_inputs[key].extend(value.split(','))
                propagated_eggs.extend(value.split(','))

        # Update options['eggs'] with found additional propagatedBuildInputs
        options = options.copy()
        options['eggs'] = '\n'.join([options.get('eggs', ''),
                                     '\n'.join(set(propagated_eggs))])

        # Save revolved egg and parsed propagatedBuildInputs
        self.egg = zc.recipe.egg.Scripts(buildout, name, options)
        self.propagated_build_inputs = propagated_build_inputs

        # Create index
        buildout = buildout.get('buildout', {}) or {}
        # noinspection PyProtectedMember
        self.index = zc.buildout.easy_install._get_index(
            (buildout.get('index', None) or '').strip() or None,
            listify(buildout.get('find-links', None) or ''),
            listify(buildout.get('allow-hosts', None) or '') or ('*',))

    def install(self):
        expressions = EXPRESSIONS.copy()
        requirements, ws = self.egg.working_set()
        packages = {}

        # Init package metadata
        for distribution in ws:
            packages[normalize(distribution.project_name)] = {
                'key': prefix(normalize(distribution.project_name)),
                'name': '%s-%s' % (distribution.project_name,
                                   distribution.version),
                'buildInputs': BUILD_INPUTS.get(distribution.project_name, []),
                'propagatedBuildInputs': []
            }

        # resolve env buildInputs and package buildInputs from buildout
        env_build_inputs = []
        for section in listify(self.options.get('build-inputs')):
            if section in self.buildout:
                for key, value in self.buildout.get(section).items():
                    key = normalize(ws.find(
                        Requirement.parse(key)).project_name)
                    packages[key]['buildInputs'] = listify(value)
            elif '=' in section:
                # is not a section, but inline mapping
                key, value = section.split('=', 1)
                key = normalize(ws.find(Requirement.parse(key)).project_name)
                packages[key].setdefault('buildInputs', [])
                packages[key]['buildInputs'].extend(value.split(','))
            else:
                # is not a section, but an environment direct buildInput
                env_build_inputs.append(section)

        # Resolve propagatedBuildInputs from package dependencies and buildout
        for project_name, requires in resolve_dependencies(
                map(Requirement.parse, requirements), ws,
                dict([(normalize(key), map(Requirement.parse, value))
                      for key, value
                      in self.propagated_build_inputs.items()])).items():
            packages[normalize(project_name)]['propagatedBuildInputs'] = \
                map(prefix, map(normalize, requires))

        # Parse package download urls and md5s from buildout
        for project_name, url in URLS.items():
            packages[normalize(project_name)]['url'] = url
        for section in listify(self.options.get('urls')):
            if section in self.buildout:
                for key, value in self.buildout.get(section).items():
                    key = normalize(ws.find(
                        Requirement.parse(key)).project_name)
                    if '#' in value:
                        url, md5 = spliturl(value.strip())
                        packages[key]['url'] = url
                        packages[key]['md5'] = md5
            elif '=' in section:
                # is not a section, but inline mapping
                key, value = section.split('=', 1)
                key = normalize(ws.find(Requirement.parse(key)).project_name)
                if '#' in value:
                    url, md5 = spliturl(value.strip())
                    packages[key]['url'] = url
                    packages[key]['md5'] = md5

        # Parse package to nixpkgs mapping from buildout
        nixpkgs = dict([(normalize(key), value) for key, value
                        in NIXPKGS.copy().items()])
        for section in listify(self.options.get('nixpkgs')):
            if section in self.buildout:
                for key, value in self.buildout.get(section).items():
                    key = normalize(ws.find(
                        Requirement.parse(key)).project_name)
                    nixpkgs[key] = ' '.join(listify(value))
            elif '=' in section:
                # is not a section, but inline mapping
                key, value = section.split('=', 1)
                key = normalize(ws.find(Requirement.parse(key)).project_name)
                nixpkgs[key] = ' '.join(value.split(','))

        output = """\
with import <nixpkgs> {};
let dependencies = rec {
"""
        for distribution in ws:

            # For mapped packages, use existing nixpkgs package instead
            if normalize(distribution.project_name) in nixpkgs:
                output += """\
  {package_name:s} = {nixpkgs_package_name:s};
""".format(package_name=prefix(normalize(distribution.project_name)),
           nixpkgs_package_name=nixpkgs[normalize(distribution.project_name)])
                continue

            # Build expression for package
            data = packages[normalize(distribution.project_name)]

            # Resolve URL and MD5
            if 'url' not in data or 'md5' not in data:
                requirement = Requirement.parse(
                    '{0:s}=={1:s}'.format(distribution.project_name,
                                          distribution.version))

                # noinspection PyProtectedMember
                indexes = zc.buildout.easy_install._indexes.values()
                indexes.remove(self.index)  # move our index to last

                for index in indexes + [self.index]:
                    if 'url' in data:
                        break

                    if index is self.index:
                        index.obtain(requirement)

                    for dist in index[requirement.key]:
                        if dist in requirement:
                            url, md5 = spliturl(dist.location)

                            if not SDIST_URL.match(url):
                                continue

                            if dist.location.startswith('http'):
                                data['url'], data['md5'] = url, md5
                                if not self.allow_from_cache:
                                    break

                            if self.allow_from_cache and \
                                    os.path.isfile(dist.location):
                                data['url'], data['md5'] = url, md5
                                data['url'] = 'file://' + data['url']
                                break

                assert data['url'], \
                    "Distribution {0:s}-{1:s} not found".format(
                        distribution.project_name, distribution.version)

                if not data['md5']:
                    md5 = hashlib.md5()
                    md5.update(urllib.urlopen(data['url']).read())
                    data['md5'] = md5.hexdigest()

            # Resolve extra expressions
            data['extras'] = filter(bool, [
                expressions.pop(req, '') for req in data['buildInputs']])

            # Build substitution dictionary
            substitutions = dict(
                key=data['key'], name=data['name'],
                url=data['url'], md5=data['md5'],
                buildInputs='\n      '.join(data['buildInputs']),
                propagatedBuildInputs=
                '\n      '.join(data['propagatedBuildInputs']),
                extras='\n'.join(data['extras']))

            output += """\
  {key:s} = buildPythonPackage {{
    name = "{name:s}";
    src = fetchurl {{
        url = "{url:s}";
        md5 = "{md5:s}";
    }};
    buildInputs = [
      {buildInputs:s}
    ];
    propagatedBuildInputs = [
      {propagatedBuildInputs:s}
    ];
    doCheck = false;
  }};
{extras:s}""".format(**substitutions)

        # Filter direct requirements
        requirements = [ws.find(Requirement.parse(req)).project_name
                        for req in requirements
                        if req in self.options.get('eggs', '')]

        # Build substitution dictionary
        substitutions = dict(
            name=self.name,
            paths='\n    '.join(env_build_inputs),
            extraLibs='\n        '.join(
                map(prefix, map(normalize, set(requirements)))),
            buildInputs='\n    '.join(
                map(prefix, map(normalize, set(requirements)))
                + env_build_inputs))

        filename = self.prefix + '.nix'
        if not self.outputs or filename in self.outputs:
            with open(filename, 'w') as handle:
                handle.write(output + """\
}};
in with dependencies; stdenv.mkDerivation {{
  name = "{name:s}";
  buildInputs = [
    {buildInputs:s}
  ];
}}
""".format(**substitutions))

        filename = self.prefix + '-env.nix'
        if not self.outputs or filename in self.outputs:
            with open(filename, 'w') as handle:
                handle.write(output + """\
}};
in with dependencies; buildEnv {{
  name = "{name:s}";
  paths = [
    {paths:s}
    (python.buildEnv.override {{
      ignoreCollisions = true;
      extraLibs = [
        {extraLibs:s}
      ];
    }})
  ];
}}
""".format(**substitutions))

        for req in requirements:
            filename = self.prefix + '-{0:s}.nix'.format(normalize(req))
            if not self.outputs or filename in self.outputs:
                with open(filename, 'w') as handle:
                    handle.write(output + """\
}};
in with dependencies; {key:s}
""".format(key=prefix(normalize(req))))

        return ()

    update = install
