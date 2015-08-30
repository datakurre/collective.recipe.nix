collective.recipe.nix
=====================

This is an experimental buildout recipe for creating nix expression from
a buildout eggs list. This is work in progress. Please, contribute_.

.. _contribute: https://github.com/datakurre/collective.recipe.nix

The minimal buildout part should include ``recipe`` and ``eggs``:

.. code:: ini

   [releaser]
   recipe = collective.recipe.nix
   eggs = zest.releaser[recommended]

The recipe generates three kind of expressions:

* mkDerivation based [name].nix usable with nix-shell and nix-build
* buildEnv based [name]-env.nix usable with nix-build
* buildPythonPackage based [name]-[package].nix usable with nix-env -i -f

Fo large projects like Plone, it's recommended to use a local mirrored package
``index`` / ``find-links`` to avoid connection issues when recipe is resolving
each package fetchurl information. Possible remedies include setting
``allow-from-cache`` to ``true`` to allow recipe to use configured buildout
download cache (and create ``file://`` urls), or just running the buildout
again with help of recipe created cumulative cache
(``[~/][.]collective.recipe.nix.cfg``).

**Known issue:** If a requirement package has setup dependencies defined in
``setup_requires``, those must be defined manually using
*propagated-build-inputs* option for this recipe.


Recipe options
--------------

**eggs**
  list of packages to generate expressions for

**name**
  string to define the name used in the resulting derivation and in the
  generated filenames (defaults to part name)

**prefix**
  string to set prefix (or path) for generated outputs (defaults to working
  directory)

**parts**
  list of existing buildout sections to install in mkDerivation based expression
  (defaults to all but the current section)

**outputs**
  list of full generated expression filenames to filter outputs to be generated
  (defaults to nothing to generate all)

**allow-from-cache**
  boolean (``true``) to allow generated expression to use package  from
  buildout download cache (defaults to ``false``)

**build-inputs**
  list of additional build-inputs from nixpkgs for generated expressions (to be
  available in nix-shell environment) or list of ``package=nixpkgsPackage``
  mappings to inject build-inputs for each package's
  ``buildPythonPackage``-expression

**propagated-build-inputs**
  list of ``package=other.package`` mappings to inject additional
  requirements for packages (usually to enable some additional features)

**nixpkgs**
  list of ``package=pythonPackages.package`` mappings to use existing packages
  from nixpkgs instead of generating custom ``buildPythonPackage`` (useful with
  package like Pillow, which need additional care to get built properly)

**urls**
  list of ``package=url#md5=hash`` mappings to explicitly define package
  download URL and MD5 checksum for cases where the recipe fails to resolve
  it automatically

`See the project repository for configuration examples.`__

__ https://github.com/datakurre/collective.recipe.nix/tree/master/examples


Example of generic use
----------------------

At first, define ``./default.nix`` with buildout::

    with import <nixpkgs> {};
    stdenv.mkDerivation {
      name = "myEnv";
      buildInputs = [
        libxml2
        libxslt
        pythonPackages.ldap
        pythonPackages.pillow
        pythonPackages.readline
        pythonPackages.zc_buildout_nix
      ];
      shellHook = ''
        export SSL_CERT_FILE=~/.nix-profile/etc/ca-bundle.crt
      '';
    }

And example ``./buildout.cfg``:

.. code:: cfg

    [buildout]
    parts = releaser

    [releaser]
    recipe = collective.recipe.nix
    eggs = zest.releaser[recommended]

Run the buildout:

.. code:: bash

   $ nix-shell --run buildout-nix

Now you should be able to run zest.releaser with recommended plugins with:

.. code:: bash

   $ nix-shell releaser.nix --run fullrelease

Or install zest.releaser into your current Nix profile with:

.. code:: bash

   $ nix-env -i -f releaser-zest_releaser.nix

`See the project repository for more configuration examples.`__

__ https://github.com/datakurre/collective.recipe.nix/tree/master/examples


Example of building Plone
-------------------------

Together with nixpkgs optimized buildout version (available in nixpkgs), this
recipe can be used to build a Nix derivation using buildout install as in Nix
derivation builder (see the generated mkDerivation based expression for
current example implementation):

.. code:: ini

   [buildout]
   extends = https://dist.plone.org/release/5-latest/versions.cfg
   parts = plone
   versions = versions

   [instance]
   recipe = plone.recipe.zope2instance
   eggs = Plone
   user = admin:admin
   environment-vars =
       PTS_LANGUAGES en
       zope_i18n_allowed_languages en
   var = /tmp

   [plone]
   recipe = collective.recipe.nix
   parts = instance
   eggs = ${instance:eggs}
   outputs = plone.nix

   [versions]
   Pillow =
   setuptools =
   zc.buildout =
   zc.recipe.egg =

.. code:: bash

   $ nix-shell --run buildout-nix
   $ nix-build plone.nix -o plone
   $ plone/bin/instance fg
