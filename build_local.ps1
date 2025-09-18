
param(
  [switch]$NoConsole
)
Write-Host "== PhoenixR1 Flasher: Local Build =="
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install mtkclient pyinstaller
if ($NoConsole) {
  pyinstaller --noconsole --onefile gui_app.py -n PhoenixR1_Flasher --icon assets\phoenix.ico
} else {
  pyinstaller --onefile gui_app.py -n PhoenixR1_Flasher --icon assets\phoenix.ico
}
Write-Host "Build complete. See dist\PhoenixR1_Flasher.exe"
