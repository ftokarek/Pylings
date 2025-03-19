#!/usr/bin/env bash

# install.sh: Setup script for Pylings
# This script detects the operating system, installs required dependencies, and sets up a virtual environment.

set -e

# Detect OS
OS=$(uname)

# Path to venv/<bin/Scripts>/activate
ACTIVATE_SCRIPT=""

# Path to virutal python
VENV_PYTHON=""

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

# Add alias to the venv activation script
set_venv_vars() {

    if [[ "$OS" =~ CYGWIN*|MINGW*|MSYS* ]]; then
        ACTIVATE_SCRIPT="venv/Scripts/activate"
        VENV_PYTHON="venv/Scripts/python"
    else
        ACTIVATE_SCRIPT="venv/bin/activate"
        VENV_PYTHON="venv/bin/python"
    fi

    PYTHON_ENV_VAR="export PYTHON="${VENV_PYTHON}""
    ALIAS_CMD="alias pylings=\"$VENV_PYTHON pylings.py\""

    echo "$ALIAS_CMD" >> "$ACTIVATE_SCRIPT"
    
    echo -e "\n# path to python used by pylings" >> "$ACTIVATE_SCRIPT"
    echo -e "$PYTHON_ENV_VAR" >> "$ACTIVATE_SCRIPT"

    echo -e "firsttime=true" > "venv/.firsttime"
}

# Install Python dependencies inside the venv
install_dependencies() {
    if [ -f "requirements.txt" ]; then
        echo "Installing Python dependencies in virtual environment..."
        $VENV_PYTHON -m pip install -r requirements.txt
    else
        echo "No requirements.txt found. Skipping Python dependencies installation."
    fi
}

# Print completion message
print_completion() {
    echo
    echo "✅ Pylings setup complete!"
    echo
    echo "📌 To manually enter the virtual environment again later, use:"
    echo -e "\n\t source ${ACTIVATE_SCRIPT}"
    echo
    echo "📌 To exit the virtual environment, type:"
    echo -e "\n\t deactivate"
    echo
    echo "You can now run Pylings using:"
    echo -e "\n\t pylings  # Alias for ${VENV_PYTHON} pylings.py"
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
set_venv_vars
install_dependencies

print_completion