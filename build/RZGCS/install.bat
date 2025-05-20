@echo off 
echo Installation der RZ Ground Control Station... 
echo Diese Installation setzt voraus, dass Python 3.8 oder höher installiert ist. 
cd /d %~dp0 
python -m pip install -r requirements.txt 
echo. 
echo Installation abgeschlossen! 
echo Sie können die Anwendung jetzt über 'start_rzgcs.bat' starten. 
pause 
