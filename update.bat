@echo off
python "%~dp0scripts\get_variants.py"
python "%~dp0scripts\update_db.py"
pause