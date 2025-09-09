{
  description = "DevShell for Riko Project";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.05";
  };

  outputs = { self, nixpkgs }: let
    system = "x86_64-linux";
    pkgs = import nixpkgs {
      inherit system;
      config = {
        allowUnfreePredicate = pkg: builtins.elem (pkgs.lib.getName pkg) [ "nvidia-x11" ];
      };
    };
  in {
    devShells.${system}.default = pkgs.mkShell {
      name = "riko-devshell";

      buildInputs = [
        pkgs.python310
        pkgs.ffmpeg_6
        pkgs.portaudio
        pkgs.git
        pkgs.linuxPackages.nvidia_x11
      ];

      shellHook = ''
        echo "Welcome to Riko DevShell!"
        export VENV_DIR=$PWD/.venv
        export UV_PYTHON=$VENV_DIR/bin/python

        # Create venv if it doesn't exist
        if [ ! -d "$VENV_DIR" ]; then
          echo "Creating Python virtual environment..."
          ${pkgs.python310}/bin/python3 -m venv $VENV_DIR
        fi

        # Activate venv
        . $VENV_DIR/bin/activate

        # Install Python dependencies if not already installed
        if [ ! -f "$VENV_DIR/.requirements_installed" ]; then
          echo "Installing Python dependencies..."
          pip install --upgrade pip
          pip install -r requirements.txt
          pip install -r extra-req.txt
          touch $VENV_DIR/.requirements_installed
        fi
      '';
    };
  };
}
