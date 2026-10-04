{
  description = "CMP-4004 week 0 dev shell";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs =
    { self, nixpkgs }:
    let
      systems = [
        "x86_64-linux"
        "aarch64-linux"
        "x86_64-darwin"
        "aarch64-darwin"
      ];
      forAllSystems = nixpkgs.lib.genAttrs systems;
      pkgsFor = system: nixpkgs.legacyPackages.${system};
    in
    {
      devShells = forAllSystems (
        system:
        let
          pkgs = pkgsFor system;
        in
        {
          default = pkgs.mkShell {
            packages = [
              (pkgs.python313.withPackages (ps: [
                ps.numpy
                ps.matplotlib
                ps.pytest
                ps.ipykernel
              ]))
            ];

            shellHook = ''
              export PYTHONPATH="$PWD:$PYTHONPATH"

              # Register this shell's python (the one with numpy/matplotlib/
              # pytest/ipykernel) as a Jupyter kernel, so `jupyter lab` uses
              # it instead of the system kernel that lacks these libs.
              PYTHON_BIN="$(command -v python3)"
              KERNEL_DIR="$HOME/.local/share/jupyter/kernels/cmp4004"
              mkdir -p "$KERNEL_DIR"
              cat > "$KERNEL_DIR/kernel.json" <<EOF
              {
                "argv": ["$PYTHON_BIN", "-m", "ipykernel_launcher", "-f", "{connection_file}"],
                "display_name": "CMP-4004 (nix shell)",
                "language": "python"
              }
              EOF

              echo "CMP-4004 dev shell ($(python3 --version))"
              echo "  python -m aicourse.doctor   # environment check"
              echo "  jupyter lab                 # then pick kernel: CMP-4004 (nix shell)"
            '';
          };
        }
      );
    };
}
