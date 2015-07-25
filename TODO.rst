* [x] auto-cache resolved fetchurl data into configparser locatable
      ini in [urls] with package-version = url#md5=hash

* [x] resolved and fetch buildout extends so that they will be
      included in nix package hash and buildout-nix in nix builder
      can be run in offline-mode

* [ ] option to auto-compile all found po files in python packages to
      ensure that resulting python packages have built mo files
