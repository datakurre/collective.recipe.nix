Changelog
=========

0.16.0 (2015-07-25)
-------------------

- Add hooks-option to inject build hook scripts into expressions
  [datakurre]

0.15.1 (2015-07-25)
-------------------

- Cleanup generated expression
  [datakurre]

0.15.0 (2015-07-25)
-------------------

- Fix to cache resolved fetchurl details between builds into
  [~/][.]collective.recipe.nix.cfg to ease creating expressions for
  large projects
  [datakurre]
- Add support for Python 3
  [datakurre]

0.14.1 (2015-07-24)
-------------------

- Fix issue where buildout provided propagatedBuildInputs were not always included
  [datakurre]

0.14.0 (2015-07-24)
-------------------

- Remove default nixpkgs mapping for lxml to allow custom lxml versions by
  default
  [datakurre]

0.13.2 (2015-07-24)
-------------------

- Fix regression where Nix-installed packages where thought to be developed
  packages
  [datakurre]

0.13.1 (2015-07-23)
-------------------

- Fix issue where generated expression was missing $src
  [datakurre]

0.13.0 (2015-07-23)
-------------------

- Fix to exclude developed packages from created expressions
  [datakurre]
- Add zc.buildout -> zc_buildout_nix to default nixpkgs mapping
  [datakurre]

0.12.1 (2015-07-23)
-------------------

- Cleanup generated [name].nix expression
  [datakurre]

0.12.0 (2015-07-23)
-------------------

- Add support for installing the configured buildout with nix
  in the generated [name].nix expression
  [datakurre]

0.11.0 (2015-07-23)
-------------------

- Change package lookup to use setuptools package index
  [datakurre]
- Add allow-from-cache option to distributions from from download-cache
  [datakurre]
- Add prefix option to control output paths
  [datakurre]
- Add outputs option to filter generated outputs
  [datakurre]
- Fix issue where nixpkgs mapping lookup failed because of non-normalize
  preconfigured mappings
  [datakurre]

0.10.1 (2015-07-23)
-------------------

- Fix typo
  [datakurre]

0.10.0 (2015-07-22)
-------------------

- Fix issue where nixpkgs mappings lookup failed because of non-normalized
  lookup
  [datakurre]
- Add support for name option to change the base name for created expressions
  [datakurre]

0.9.3 (2015-07-22)
------------------

- Fix a few more issues where package was not found at PyPI
  [datakurre]

0.9.2 (2015-07-12)
------------------

- Fix a few issues where package was not found at PyPI
  [datakurre]

0.9.1 (2015-07-11)
------------------

- Fix issue where package requirement in wrong case caused error
- Fix issue where buildout propagated-build-inputs did not support
  cyclic requirements (required for injecting 'add-on' packages)
  [datakurre]

0.9.0 (2015-07-10)
------------------

- Refactor to handle properly setuptools requires extras
  [datakurre]

0.8.0 (2015-07-10)
------------------

- Add support for comma separated list for inline build-inputs,
  propagated-build-inputs and nixpkgs
  [datakurre]

0.7.0 (2015-07-10)
------------------

- Add option to inject propagatedBuildInputs to enable extra package-dependent
  additional features
  [datakurre]

0.6.0 (2015-07-10)
------------------

- Add to create installable python package expression for each listed egg
  [datakurre]

0.5.0 (2015-07-09)
------------------

- Fix to resolve cyclic dependencies by letting the first seen dependency win
  and persist into resulting expression
  [datakurre]

0.4.0 (2015-07-09)
------------------

- Change to produce {name}-env.nix instead of {name}.env.nix as buildable
  derivations
  [datakurre]

0.3.0 (2015-07-08)
------------------

- Change resulting derivation to be buildEnv with python.buildEnv to make it
  also nix-buildable
  [datakurre]

0.2.0 (2015-07-08)
------------------

- Add buildout-based configuration
  [datakurre]
- Back to development: 0.1.2
  [datakurre]

0.1.1 (2015-07-08)
------------------

- Add support for plone.app.ldap
  [datakurre]

0.1.0 (2015-07-08)
------------------

- Proof of concept release.

