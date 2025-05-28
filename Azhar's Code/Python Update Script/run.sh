#!/bin/zsh

# Activate virtual environment
source venv/bin/activate

# Install requirements if they haven't been installed
if [ ! -f "venv/.requirements_installed" ]; then
    echo "Installing requirements..."
    pip install -r requirements.txt
    playwright install firefox
    touch venv/.requirements_installed
fi

# Run the script
python fullUpdateLoopOriginal.py

# Deactivate virtual environment
deactivate
