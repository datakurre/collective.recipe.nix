Changelog
=========

0.9.3 (unreleased)
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

