@echo off
REM Atalho para iniciar o Jarvis com duplo-clique.
REM Entra na pasta do script e roda usando o Python do ambiente virtual.
cd /d "%~dp0"
".venv\Scripts\python.exe" main.py
pause
