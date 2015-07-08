collective.recipe.nix
=====================

This is an experimental buildout recipe for creating nix expression from
a buildout eggs list. This is work in progress. Please, contribute_.

.. _contribute: https://github.com/datakurre/collective.recipe.nix

**This only works, for now, when all packages are available at PyPI.**

Example of usage
----------------

At first, define ``./default.nix`` with buildout::

    with import <nixpkgs> {}; {
      myEnv = stdenv.mkDerivation {
        name = "myEnv";
        buildInputs = [
          pythonPackages.readline
          pythonPackages.buildout
        ];
        shellHook = ''
          export SSL_CERT_FILE=~/.nix-profile/etc/ca-bundle.crt
        '';
      };
    }

And example ``./buildout.cfg``:

.. code:: cfg

    [buildout]
    extends = https://dist.plone.org/release/4-latest/versions.cfg
    parts =
        plone
        zest.releaser
    develop = .
    versions = versions

    [instance]
    recipe = plone.recipe.zope2instance
    eggs = Plone
    user = admin:admin

    [plone]
    recipe = collective.recipe.nix
    eggs =
        ${instance:eggs}
        plone.recipe.zope2instance

    [zest.releaser]
    recipe = collective.recipe.nix
    eggs = zest.releaser

    [versions]
    zc.buildout =
    setuptools =

Run the buildout:

.. code:: bash

   $ nix-shell --run buildout

Now you should be able to run zest.releaser with:

.. code:: bash

   $ nix-shell zest.releaser.nix --run fullrelease

And launching python with all Plone dependencies (after removing
buildout created site.py to remove references from buildout installed
eggs) with:

.. code:: bash

   $ rm -f parts/instance/site.py parts/instance/site.pyc
   $ nix-shell plone.nix --run python

And Plone could be started by entering the following lines into the
interpreter:

.. code:: python

    import plone.recipe.zope2instance.ctl
    plone.recipe.zope2instance.ctl.main(['-C', 'parts/instance/etc/zope.conf', 'fg'])
