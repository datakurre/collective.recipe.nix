with import <nixpkgs> {};
stdenv.mkDerivation {
  name = "build";
  buildInputs = [
    libxml2
    libxslt
    pythonPackages.ldap
    pythonPackages.pillow
    pythonPackages.readline
    (pythonPackages.zc_buildout_nix.overrideDerivation (args: { postInstall = ""; }))
  ];
  shellHook = ''
    export SSL_CERT_FILE=${cacert}/etc/ssl/certs/ca-bundle.crt
  '';
}
