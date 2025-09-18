@echo off
REM Build script for PhoenixR1 Flasher
REM Requires Python 3.11 and the packages in requirements.txt
setlocal

where py >nul 2>&1 || (
  echo Python launcher (py) not found. Install Python 3.11 from https://www.python.org/
  exit /b 1
)

py -3.11 -m venv venv
call venv\Scripts\activate

python -m pip install --upgrade pip
pip install -r requirements.txt

REM Build single-file exe, console hidden
pyinstaller --onefile --noconsole gui_app.py -n PhoenixR1_Flasher --icon assets\phoenix.ico

echo.
echo Build complete. Find your EXE at .\dist\PhoenixR1_Flasher.exe
echo.

endlocal
