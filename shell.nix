{ pkgs ? import <nixpkgs> {} }:

let
  pythonEnv = pkgs.poetry2nix.mkPoetryEnv {
    python = pkgs.python3;
    poetrylock = ./poetry.lock;
  };
in pkgs.mkShell {
  buildInputs = with pkgs; [
    poetry
    python3Packages.wand
    python3Packages.magic
  ];
}
