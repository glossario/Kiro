@echo off
REM Atalho para iniciar o Jovem Aprendiz com duplo-clique.
REM Entra na pasta do script e roda usando o Python do ambiente virtual.
cd /d "%~dp0"

REM Garante que o microfone nao esteja preso pelo Teams rodando em 2o plano.
REM (comente a linha abaixo se nao quiser que o atalho feche o Teams)
taskkill /IM ms-teams.exe /F >nul 2>&1

".venv\Scripts\python.exe" main.py
echo.
echo ---------------------------------------------
echo Se aparecer erro de microfone acima, feche o Teams/Zoom/Meet e rode de novo.
echo ---------------------------------------------
pause
