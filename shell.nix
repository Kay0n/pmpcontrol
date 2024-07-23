{ pkgs ? import <nixpkgs> {} }:
(pkgs.buildFHSEnv  {
  name = "python-env";
  targetPkgs = pkgs: (with pkgs; [
    python312Full
    python312Packages.pip
    python312Packages.virtualenv
    # libgcc
    # binutils
    # coreutils
    # expat
    # libz
    alsa-lib
  ]);
  multiPkgs = pkgs: (with pkgs; [ ]);
  runScript = ''
    #!/bin/sh
    if [ ! -d .venv ]; then
      echo "Creating virtual environment..."
      python -m venv .venv
    fi
    . .venv/bin/activate
    exec zsh
  '';
}).env
  