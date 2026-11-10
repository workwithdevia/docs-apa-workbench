{
  description = "APA Workbench development environment (Typst + uv)";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = { nixpkgs, ... }:
    let
      supportedSystems = [
        "x86_64-linux"
        "aarch64-linux"
      ];

      forAllSystems = nixpkgs.lib.genAttrs supportedSystems;
      lib = nixpkgs.lib;
    in
    {
      devShells = forAllSystems (system:
        let
          pkgs = import nixpkgs {
            inherit system;
          };

          fontPackages = [
            pkgs.nerd-fonts.hack
            pkgs.dejavu_fonts
          ];

          fontPaths = map (font: "${font}/share/fonts") fontPackages;

        in
        assert lib.versionAtLeast pkgs.typst.version "0.15.0";
        assert lib.versionAtLeast pkgs.python3.version "3.11";
        {
          default = pkgs.mkShell {
            name = "apa-workbench-dev";

            packages = [
              # Typst document compiler.
              pkgs.typst

              # Python dependency and environment manager.
              pkgs.uv
              pkgs.python3

              # Repository and shell utilities.
              pkgs.git
              pkgs.bash
              pkgs.coreutils
              pkgs.findutils
              pkgs.gnugrep
              pkgs.gawk
              pkgs.gnused
              pkgs.gnutar
              pkgs.xz
              pkgs.zip
              pkgs.unzip
              pkgs.ripgrep

              # Font discovery and project fonts.
              pkgs.fontconfig
              pkgs.nerd-fonts.hack
              pkgs.dejavu_fonts

              # Nix formatter.
              pkgs.nixfmt-rfc-style
            ];

            # Force uv to use the Nix-provided interpreter. This prevents
            # downloading a generic Linux Python that may not run on NixOS.
            UV_PYTHON = "${pkgs.python3}/bin/python3";
            UV_PYTHON_DOWNLOADS = "never";

            # Typst searches these additional font directories.
            TYPST_FONT_PATHS = lib.concatStringsSep ":" fontPaths;

            # uv owns the project virtual environment (.venv).
            UV_PROJECT_ENVIRONMENT = ".venv";
            UV_LINK_MODE = "copy";
            UV_NO_PROGRESS = "1";

            shellHook = ''
              echo ""
              echo "APA Workbench development environment"
              echo "--------------------------------------"
              echo "$(typst --version)"
              echo "$(uv --version)"
              echo "Python interpreter: $UV_PYTHON"
              echo "Hack Nerd Font and DejaVu fonts: available to Typst"
              echo ""
              echo "Run all checks: ./scripts/test-local.sh"
              echo "Sync Python tools: uv sync"
              echo "Update dependency lock: uv lock"
              echo "Format Nix: nix fmt"
              echo ""
            '';
          };
        }
      );

      formatter = forAllSystems (system:
        let
          pkgs = import nixpkgs { inherit system; };
        in
        pkgs.nixfmt
      );
    };
}
