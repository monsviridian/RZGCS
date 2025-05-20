@echo off 
echo Erstelle Desktop-Verknüpfung... 
cd /d %~dp0 
echo Set oWS = WScript.CreateObject("WScript.Shell") 
echo sLinkFile = oWS.SpecialFolders("Desktop") & "\RZ Ground Control Station.lnk" 
echo Set oLink = oWS.CreateShortcut(sLinkFile) 
echo oLink.TargetPath = oWS.CurrentDirectory & "\start_rzgcs.bat" 
echo oLink.IconLocation = oWS.CurrentDirectory & "\Assets\icon.ico" 
echo oLink.WindowStyle = 1 
echo oLink.WorkingDirectory = oWS.CurrentDirectory 
echo oLink.Description = "RZ Ground Control Station" 
echo oLink.Save 
cscript //nologo "C:\Users\fuckheinerkleinehack\AppData\Local\Temp\shortcut.vbs" 
del "C:\Users\fuckheinerkleinehack\AppData\Local\Temp\shortcut.vbs" 
echo Desktopverknüpfung erstellt! 
pause 
