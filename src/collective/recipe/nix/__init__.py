# -*- coding: utf-8 -*-
import operator
import re
import xmlrpclib
import zc.recipe.egg


def canonical(s):
    return '_' + re.sub('[\.\-\s]', '_', s)


class Nix(object):

    def __init__(self, buildout, name, options):
        self.egg = zc.recipe.egg.Scripts(buildout, name, options)
        self.name = name
        self.options = options

    def install(self):
        pypi = xmlrpclib.ServerProxy('https://pypi.python.org/pypi')
        requirements, ws = self.egg.working_set()
        with open(self.name + '.nix', 'w') as output:
            output.write("""\
with import <nixpkgs> {};
let dependencies = rec {
""")
            for package in ws:
                urls = [url for url in pypi.release_urls(package.project_name,
                                                         package.version)
                        if url['url'].endswith('.tar.gz')
                        or url['url'].endswith('.zip')]
                details = dict(
                    name=canonical(package.project_name),
                    package='%s-%s' % (package.project_name, package.version),
                    url=urls[0]['url'],
                    md5=urls[0]['md5_digest'],
                    inputs=' '.join(map(canonical, map(operator.attrgetter('project_name'),
                                                       package.requires()))))
                output.write("""\
  {name:s} = buildPythonPackage {{
    name = "{package:s}";
    src = fetchurl {{
        url = "{url:s}";
        md5 = "{md5:s}";
    }};
    propagatedBuildInputs = [
        {inputs:s}
    ];
    doCheck = false;
  }};
""".format(**details))

            output.write("""\
}};
in with dependencies; stdenv.mkDerivation {{
  name = "{name:s}";
  buildInputs = [
    {inputs:s}
  ];
}}
""".format(name='temp', inputs=' '.join(map(canonical, requirements))))
        return ()

    update = install
