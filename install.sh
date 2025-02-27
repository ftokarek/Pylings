#!/usr/bin/env bash

# install.sh: Setup script for Pylings
# This script detects the operating system, installs required dependencies, and sets up a virtual environment.

set -e

# Detect OS
OS=$(uname)

# Detect Python Interpreter (after OS detection)
detect_python() {
    if [[ "$OS" =~ CYGWIN*|MINGW*|MSYS* ]] && command -v py &>/dev/null; then
        echo "py"
    elif command -v python3 &>/dev/null; then
        echo "python3"
    else
        echo ""
    fi
}

# Install Python if missing
install_python() {
    echo "Installing Python dependencies..."
    case "$OS" in
        Linux)
            sudo apt update && sudo apt install -y python3 python3-venv python3-pip
            ;;
        Darwin)
            brew install python3
            ;;
        *)
            echo "Unsupported OS or manual installation required. Install Python from https://www.python.org/"
            exit 1
            ;;
    esac
}

# Setup virtual environment
setup_venv() {
    if [ -d "venv/" ]; then
      rm -rf venv/
    fi
    echo "Creating virtual environment..."
    $PYTHON -m venv venv
}

# Get the correct Python inside venv
venv_python() {
    if [[ "$OS" =~ CYGWIN*|MINGW*|MSYS* ]]; then
        echo "venv/Scripts/python"
    else
        echo "venv/bin/python"
    fi
}

# Install Python dependencies inside the venv
install_dependencies() {
    VENV_PYTHON=$(venv_python)
    if [ -f "requirements.txt" ]; then
        echo "Installing Python dependencies in virtual environment..."
        $VENV_PYTHON -m pip install -r requirements.txt
    else
        echo "No requirements.txt found. Skipping Python dependencies installation."
    fi
}

# Add alias to the venv activation script
set_venv_vars() {
    VENV_PYTHON=$(venv_python)
    PYTHON_ENV_VAR="export PYTHON="${VENV_PYTHON}""
    ALIAS_CMD="alias pylings=\"$VENV_PYTHON pylings.py\""
    MOTD_MESSAGE='echo -e "\n\033[1;32mWelcome to Pylings!\n\nLearn Python interactively to solve exercises.\n\nThese exercises usually contain some compiler or logic errors which cause the exercise to fail compilation or testing.\n\nFind all errors and fix them!.\n\nType pylings to get started! \033[0m\n"'

    if [[ "$OS" =~ CYGWIN*|MINGW*|MSYS* ]]; then
        ACTIVATE_SCRIPT="venv/Scripts/activate"
    else
        ACTIVATE_SCRIPT="venv/bin/activate"
    fi

    echo "$ALIAS_CMD" >> "$ACTIVATE_SCRIPT"

    echo -e "\n# Custom MOTD" >> "$ACTIVATE_SCRIPT"
    echo "$MOTD_MESSAGE" >> "$ACTIVATE_SCRIPT"

    echo -e "\n# path to python used by pylings" >> "$ACTIVATE_SCRIPT"
    echo -e "$PYTHON_ENV_VAR" >> "$ACTIVATE_SCRIPT"

    echo -e "firsttime=true" > "venv/.firsttime"
}

# Print completion message
print_completion() {
    echo "✅ Pylings setup complete!"
    echo "Your virtual environment has been activated automatically."
    echo
    echo "📌 To manually enter the virtual environment again later, use:"
    echo -e "\t source venv/bin/activate  # (Linux/macOS)"
    echo -e "\t source venv/Scripts/activate   # (Windows)"
    echo
    echo "📌 To exit the virtual environment, type:"
    echo -e "\t deactivate"
    echo
    echo "You can now run Pylings using:"
    echo -e "\t pylings  # Alias for $(venv_python) pylings.py"
}

# Main execution
PYTHON=$(detect_python)

if [[ -z "$PYTHON" ]]; then
    install_python
    PYTHON=$(detect_python)
    if [[ -z "$PYTHON" ]]; then
        echo "Python installation failed. Please install it manually."
        exit 1
    fi
fi

setup_venv
install_dependencies
set_venv_vars

print_completion