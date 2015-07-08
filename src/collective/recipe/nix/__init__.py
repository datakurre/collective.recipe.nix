# -*- coding: utf-8 -*-
import re
import xmlrpclib
import zc.recipe.egg

NIXPKGS_WHITELIST = {
    'lxml': 'pythonPackages.lxml',
    'Pillow': 'pythonPackages.pillow'
}

# Zope2 has circular dependencies with its dependencies. Also Products and
# plone -namespaces have circular dependencies every now and then. To avoid
# circular depedendencies in resulting nix expression, we simply drop all
# these from propagatedBuildInputs and only add them into them into the final
# derivation. This results in broken individual packages, but still makes
# them work within the final derivation (as long as a dropped dependency
# breaks the original build of the package).
REQUIRES_BLACKLIST = re.compile('Zope2.*|Products.*|plone.*')

# Some packages require additional build input
BUILD_INPUTS = {
    'Products.DCWorkflow': ['eggtestinfo'],
    'Products.CMFUid': ['eggtestinfo'],
    'Products.CMFActionIcons': ['eggtestinfo'],
}

# And some of those required build inputs are not yet available at nixpkgs
BUILD_INPUT_DRVS = {
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

SDIST_URL = re.compile('.*tar.gz$|.*zip$')

# XXX: All above should be made configurable somehow.


def normalize(s):
    return re.sub('[\.\-\s]', '_', '_' + s)


class Nix(object):

    def __init__(self, buildout, name, options):
        self.egg = zc.recipe.egg.Scripts(buildout, name, options)
        self.name = name
        self.options = options

    def install(self):
        pypi = xmlrpclib.ServerProxy('https://pypi.python.org/pypi')
        requirements, ws = self.egg.working_set()

        build_input_drvs = BUILD_INPUT_DRVS.copy()
        requirements += filter(bool, map(
            str.strip, self.options.get('build-inputs', '').split()))

        with open(self.name + '.nix', 'w') as output:
            output.write("""\
with import <nixpkgs> {};
let dependencies = rec {
""")
            for package in ws:
                if package.project_name in NIXPKGS_WHITELIST:
                    output.write("""\
  {name:s} = {nixpkgs_name:s};
""".format(name=normalize(package.project_name),
           nixpkgs_name=NIXPKGS_WHITELIST[package.project_name]))
                    continue

                urls = [data for data in pypi.release_urls(
                        package.project_name, package.version)
                        if SDIST_URL.match(data['url'])]

                assert urls, "Package {0:s}-{1:s} not found at PyPI".format(
                    package.project_name, package.version)

                requirements += [req.project_name
                                 for req in package.requires()
                                 if REQUIRES_BLACKLIST.match(req.project_name)]

                details = dict(
                    name=normalize(package.project_name),
                    package='%s-%s' % (package.project_name, package.version),
                    url=urls[0]['url'],
                    md5=urls[0]['md5_digest'],
                    inputs='\n      '.join(
                        BUILD_INPUTS.get(package.project_name, [])
                    ),
                    requires='\n      '.join([
                        normalize(req.project_name)
                        for req in package.requires()
                        if not REQUIRES_BLACKLIST.match(req.project_name)
                    ]),
                    extras='\n'.join(filter(bool, [
                        build_input_drvs.pop(req, '')
                        for req in BUILD_INPUTS.get(package.project_name, [])
                    ])))
                output.write("""\
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
{extras:s}""".format(**details))

            output.write("""\
}};
in with dependencies; stdenv.mkDerivation {{
  name = "{name:s}";
  buildInputs = [
    {inputs:s}
  ];
}}
""".format(name=self.name, inputs='\n    '.join(map(normalize, set(requirements)))))
        return ()

    update = install
