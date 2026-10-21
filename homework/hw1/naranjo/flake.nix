{
  description = "CMP-4004 HW1 dev shell.";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs =
    { self, nixpkgs }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs { inherit system; };
    in
    {
      devShells.${system}.default = pkgs.mkShell {
        packages = [
          (pkgs.python3.withPackages (ps: [
            ps.numpy
            ps.matplotlib
            ps.pytest
            ps.ipykernel
          ]))
        ];

        shellHook = ''
          # Imports resolve from this folder's code/ directory, so every script
          # runs from either place (cd code; python3 harness.py).
          export PYTHONPATH="$PWD/code:$PYTHONPATH"

          echo "HW1 shell ($(python3 --version))"
          echo "  cd code && python3 test_search.py   # provided tests"
          echo "  cd code && python3 test_engine.py   # our engine vs the studio engines"
          echo "  cd code && python3 harness.py       # benchmark -> ../results/"
        '';
      };
    };
}
