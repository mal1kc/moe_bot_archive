# python -m nuitka --standalone --enable-plugin=tk-inter --include-plugin-directory=moe_bot\lokalizasyon  --include-plugin-directory=moe_bot\ayarlar --include-data-dir=imgs=imgs --include-data-dir=arayuz=arayuz --nofollow-import-to='*.tests' --windows-icon-from-ico=arayuz\moe_icon.ico moe_bot_program.py


# Get the path of the virtual environment
$VENV_PATH = (poetry env info -p) | Out-String -Stream | Select-Object -Last 1
echo "using venv : $VENV_PATH"

# Activate the virtual environment
& "$VENV_PATH\Scripts\activate"

# Get the path of the Python executable in the virtual environment
$PYTHON_PATH = Join-Path $VENV_PATH "Scripts\python.exe"
echo "using python : $PYTHON_PATH"

# Create the exe file with Nuitka using the virtual environment Python
& "$PYTHON_PATH" -m nuitka --standalone `
 --enable-plugin=tk-inter `
 --include-plugin-directory=moe_bot\lokalizasyon `
 --include-data-dir=imgs=imgs `
 --include-data-dir=arayuz=arayuz `
 --nofollow-import-to='*.tests' `
 --windows-icon-from-ico=arayuz\moe_icon.ico moe_bot_program.py
