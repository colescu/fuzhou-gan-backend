@echo off
python "%~dp0scripts\update_date.py"
echo -----
python "%~dp0scripts\get_variants.py"
echo -----
python "%~dp0scripts\update_FG.py"
echo -----
python "%~dp0scripts\update_ipa.py"
echo -----
python "%~dp0scripts\export_syllables.py"
python "%~dp0scripts\export_MC.py"
echo -----
python "%~dp0scripts\export_lang.py"
echo -----
pause