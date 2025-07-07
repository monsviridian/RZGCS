# Verbessertes Qt-Plugin-Fix-Skript
$venv = ".venv"
$dist = "dist\RZGCS"

Write-Host "Kopiere alle Qt-Plugins und QML-Module..." -ForegroundColor Green

# PySide6-Installation finden
$pyside6_path = "$venv\Lib\site-packages\PySide6"
if (-not (Test-Path $pyside6_path)) {
    Write-Host "PySide6 nicht gefunden in $pyside6_path" -ForegroundColor Red
    exit 1
}

# Alle wichtigen Qt-Plugins kopieren
$plugins = @(
    "platforms",
    "imageformats", 
    "iconengines",
    "qmltooling",
    "qml",
    "tls",
    "networkinformation",
    "generic",
    "minimal",
    "offscreen"
)

foreach ($plugin in $plugins) {
    $src = "$pyside6_path\$plugin"
    $dst = "$dist\$plugin"
    if (Test-Path $src) {
        Write-Host "Kopiere Plugin: $plugin" -ForegroundColor Yellow
        Copy-Item $src $dst -Recurse -Force -ErrorAction SilentlyContinue
    } else {
        Write-Host "Plugin nicht gefunden: $plugin" -ForegroundColor Red
    }
}

# QML-Module kopieren
$qml_modules = @(
    "Qt",
    "QtQml",
    "QtQuick",
    "QtQuick.2",
    "QtGraphicalEffects",
    "QtLocation",
    "QtPositioning"
)

foreach ($module in $qml_modules) {
    $src = "$pyside6_path\qml\$module"
    $dst = "$dist\qml\$module"
    if (Test-Path $src) {
        Write-Host "Kopiere QML-Modul: $module" -ForegroundColor Yellow
        New-Item -ItemType Directory -Force -Path "$dist\qml" | Out-Null
        Copy-Item $src $dst -Recurse -Force -ErrorAction SilentlyContinue
    }
}

# Zusätzliche DLLs kopieren
$additional_dlls = @(
    "Qt6Core.dll",
    "Qt6Gui.dll", 
    "Qt6Qml.dll",
    "Qt6Quick.dll",
    "Qt6Network.dll",
    "Qt6Widgets.dll",
    "Qt6OpenGL.dll",
    "Qt6OpenGLWidgets.dll"
)

foreach ($dll in $additional_dlls) {
    $src = "$pyside6_path\$dll"
    if (Test-Path $src) {
        Write-Host "Kopiere DLL: $dll" -ForegroundColor Yellow
        Copy-Item $src $dist -Force -ErrorAction SilentlyContinue
    }
}

# Shiboken6-DLLs
$shiboken_dlls = @(
    "shiboken6.abi3.dll"
)

foreach ($dll in $shiboken_dlls) {
    $src = "$venv\Lib\site-packages\shiboken6\$dll"
    if (Test-Path $src) {
        Write-Host "Kopiere Shiboken DLL: $dll" -ForegroundColor Yellow
        Copy-Item $src $dist -Force -ErrorAction SilentlyContinue
    }
}

Write-Host "Qt-Plugin-Fix abgeschlossen!" -ForegroundColor Green
Write-Host "Versuche jetzt RZGCS.exe zu starten..." -ForegroundColor Green 