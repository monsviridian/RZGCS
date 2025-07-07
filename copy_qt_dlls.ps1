# Kopiert alle nötigen Qt/PySide6-DLLs und Plugins in dist/RZGCS
$venv = ".venv"
$dist = "dist\RZGCS"

# DLL-Quellen
$pyside6 = "$venv\Lib\site-packages\PySide6"
$shiboken6 = "$venv\Lib\site-packages\shiboken6"
$numpy_libs = "$venv\Lib\site-packages\numpy.libs"

# Zielordner für DLLs
$target = $dist

Write-Host "Kopiere PySide6-DLLs..."
Copy-Item "$pyside6\*.dll" $target -Force -ErrorAction SilentlyContinue
Write-Host "Kopiere shiboken6-DLLs..."
Copy-Item "$shiboken6\*.dll" $target -Force -ErrorAction SilentlyContinue
Write-Host "Kopiere numpy.libs-DLLs..."
Copy-Item "$numpy_libs\*.dll" $target -Force -ErrorAction SilentlyContinue

# Qt-Plugins (platforms, imageformats, etc.)
$plugins = @("platforms", "imageformats", "qmltooling", "qml")
foreach ($plugin in $plugins) {
    $src = "$pyside6\$plugin"
    $dst = "$dist\$plugin"
    if (Test-Path $src) {
        Write-Host "Kopiere Plugin-Ordner: $plugin"
        Copy-Item $src $dst -Recurse -Force -ErrorAction SilentlyContinue
    }
}

Write-Host "Fertig! Prüfe, ob jetzt DLLs im dist-Ordner liegen." 