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
