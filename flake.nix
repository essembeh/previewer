{
  description = "Application packaged using poetry2nix";

  inputs.flake-utils.url = "github:numtide/flake-utils";
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  inputs.poetry2nix = {
    url = "github:nix-community/poetry2nix";
    inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs = { self, nixpkgs, flake-utils, poetry2nix }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        # see https://github.com/nix-community/poetry2nix/tree/master#api for more functions and examples.
        inherit (poetry2nix.legacyPackages.${system}) mkPoetryApplication;
        pkgs = nixpkgs.legacyPackages.${system};
      in
      {
        packages = {
          myapp = mkPoetryApplication { 
            projectDir = self;
            overrides = pkgs.poetry2nix.defaultPoetryOverrides.extend (
              self: super: {
                # use nixos version of wand since the source code is amended to work with Nix
                wand = pkgs.python3Packages.wand;
              }
            );
            # external tools called directly by app
            propagatedBuildInputs = with pkgs; [ 
              ffmpeg imagemagickBig 
            ];
          };
          default = self.packages.${system}.myapp;
        };

        devShells.default = pkgs.mkShell {
          packages = with pkgs; [
            # poetry
            poetry2nix.packages.${system}.poetry
            # external tools
            ffmpeg imagemagickBig
            # myapp
            (pkgs.poetry2nix.mkPoetryEnv { 
              projectDir = self; 
              overrides = pkgs.poetry2nix.defaultPoetryOverrides.extend (
                self: super: {
                  wand = pkgs.python3Packages.wand;
                }
              );
            })
          ];
        };
      });
}
