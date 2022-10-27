with import <nixpkgs> {};

pkgs.mkShell {
  packages = [
    (python310.withPackages (p: with p; [
      (
        buildPythonPackage rec {
          pname = "locust";
          version = "2.14.0";
          src = fetchPypi {
            inherit pname version;
            sha256 = "TVWBU1lMOltNWdhFHgOkQrS51MZRN9V2fDV106HBb8s=";
          };
          doCheck = false;
        }
      )
    ]))

    pkgs.curl
  ];
}
