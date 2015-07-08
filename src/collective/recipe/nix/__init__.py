# -*- coding: utf-8 -*-
import re
import xmlrpclib
import zc.recipe.egg

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
DERIVATIONS = {
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

# Move requirements from package to environment
REQUIRES_BLACKLIST = re.compile('Zope2.*|Products.*|plone.*')

# Zope2 has circular dependencies with its dependencies. Also Products and
# plone -namespaces have circular dependencies every now and then.  To avoid
# circular depedendencies in resulting nix expression, we simply drop all these
# from propagatedBuildInputs and only add them into them into the final
# derivation. This results in broken individual packages, but still makes them
# work within the final derivation (as long as a dropped dependency breaks the
# original build of the package).


def normalize(s):
    # Normalize given derivation name and prefix it with '_' to avoid
    # possible nixpkgs conflicts
    return re.sub('[\.\-\s]', '_', '_' + s)


def listify(s):
    return filter(bool, map(str.strip, (s or '').split()))


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
        self.egg = zc.recipe.egg.Scripts(buildout, name, options)

    def install(self):
        pypi = xmlrpclib.ServerProxy('https://pypi.python.org/pypi')
        requirements, ws = self.egg.working_set()
        derivations = DERIVATIONS.copy()

        # Parse direct buildInputs and mapped buildInputs from buildout
        build_inputs = BUILD_INPUTS.copy()
        build_inputs.setdefault(None, [])
        for section in listify(self.options.get('build-inputs')):
            if section in self.buildout:
                for key, value in self.buildout.get(section).items():
                    build_inputs[key] = listify(value)
            elif '=' in section:
                # is not a section, but inline mapping
                key, value = section.split('=', 1)
                build_inputs[key] = [value.strip()]
            else:
                # is not a section, but a direct buildInput
                build_inputs[None].append(section)

        # Parse Python package to nixpkgs mapping from buildout
        nixpkgs = NIXPKGS.copy()
        for section in listify(self.options.get('nixpkgs')):
            if section in self.buildout:
                for key, value in self.buildout.get(section).items():
                    nixpkgs[key] = ' '.join(listify(value))
            elif '=' in section:
                # is not a section, but inline mapping
                key, value = section.split('=', 1)
                nixpkgs[key] = value.strip()

        # Parse Download urls from buildout
        urls = URLS.copy()
        for section in listify(self.options.get('urls')):
            if section in self.buildout:
                for key, value in self.buildout.get(section).items():
                    if '#' in value:
                        urls[key] = value.strip()
            elif '=' in section:
                # is not a section, but inline mapping
                key, value = section.split('=', 1)
                if '#' in value:
                    urls[key] = value.strip()

        output = """\
with import <nixpkgs> {};
let dependencies = rec {
"""
        for package in ws:

            if package.project_name in nixpkgs:
                output += """\
  {name:s} = {nixpkgs_name:s};
""".format(name=normalize(package.project_name),
           nixpkgs_name=nixpkgs[package.project_name])
                continue

            if package.project_name in urls:
                url, md5 = spliturl(urls[package.project_name])
            else:
                candidates = [
                    data for data in pypi.release_urls(
                        package.project_name, package.version)
                    if SDIST_URL.match(data['url'])
                ]
                assert candidates,\
                    "Package {0:s}-{1:s} not found at PyPI".format(
                        package.project_name, package.version)
                url = candidates[0]['url']
                md5 = candidates[0]['md5_digest']

            requirements += [
                req.project_name for req in package.requires()
                if REQUIRES_BLACKLIST.match(req.project_name)
            ]

            substitutions = dict(
                name=normalize(package.project_name),
                package='%s-%s' % (package.project_name, package.version),
                url=url, md5=md5,
                inputs='\n      '.join(
                    build_inputs.get(package.project_name, [])
                ),
                requires='\n      '.join([
                    normalize(req.project_name)
                    for req in package.requires()
                    if not REQUIRES_BLACKLIST.match(req.project_name)
                ]),
                derivations='\n'.join(filter(bool, [
                    derivations.pop(req, '')
                    for req in build_inputs.get(package.project_name, [])
                ])))

            output += """\
  {name:s} = buildPythonPackage {{
    name = "{package:s}";
    src = fetchurl {{
        url = "{url:s}";
        md5 = "{md5:s}";
    }};
    buildInputs = [
      {inputs:s}
    ];
    propagatedBuildInputs = [
      {requires:s}
    ];
    doCheck = false;
  }};
{derivations:s}""".format(**substitutions)

        substitutions = dict(
            name=self.name,
            paths='\n    '.join(build_inputs[None]),
            extraLibs='\n        '.join(map(normalize, set(requirements))),
            buildInputs='\n      '.join(map(normalize, set(requirements))
                                        + build_inputs[None])
        )

        with open(self.name + '.nix', 'w') as handle:
            handle.write(output + """\
}};
in with dependencies; stdenv.mkDerivation {{
  name = "{name:s}";
  buildInputs = [
    {buildInputs:s}
  ];
}}
""".format(**substitutions))

        with open(self.name + '-env.nix', 'w') as handle:
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

        return ()

    update = install
