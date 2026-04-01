{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = [
    pkgs.python313
    pkgs.python313Packages.pygame-ce
  ];

  shellHook = ''
    echo "Run 'python3 main.py' to run it."
    echo "Edit the source code to select a simulation."
  '';
}
