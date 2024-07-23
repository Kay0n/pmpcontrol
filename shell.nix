{ pkgs ? import <nixpkgs> {} }:

(pkgs.buildFHSEnv  {
  name = "python-env";
  targetPkgs = pkgs: (with pkgs; [
    python312Full
    python312Packages.pip
    python312Packages.virtualenv
    alsa-lib
  ]);
  multiPkgs = pkgs: (with pkgs; [ ]);
  runScript = ''
    #!/bin/sh
    if [ ! -d .venv ]; then
      python -m venv .venv
    fi
    if which zsh &> /dev/null
    then
        exec zsh
    else
        exec $SHELL
    fi
  '';
}).env
  