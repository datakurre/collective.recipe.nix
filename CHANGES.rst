Changelog
=========

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

