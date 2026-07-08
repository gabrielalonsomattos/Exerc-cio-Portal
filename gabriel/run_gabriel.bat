@echo off
setlocal EnableExtensions EnableDelayedExpansion

cd /d "%~dp0"

set "VENV_DIR=.venv"
set "VENV_PY=%VENV_DIR%\Scripts\python.exe"
set "REQ_FILE=requirements.txt"
set "SCRIPT=buscar_cpf_gabriel.py"

if not exist "%VENV_PY%" (
  echo [INFO] Criando ambiente virtual...
  where py >nul 2>nul
  if %errorlevel%==0 (
    py -3 -m venv "%VENV_DIR%"
  ) else (
    python -m venv "%VENV_DIR%"
  )
)

if not exist "%VENV_PY%" (
  echo [ERRO] Nao foi possivel criar o ambiente virtual.
  pause
  exit /b 1
)

echo [INFO] Instalando dependencias...
"%VENV_PY%" -m pip install --upgrade pip >nul
"%VENV_PY%" -m pip install -r "%REQ_FILE%" >nul
"%VENV_PY%" -m playwright install chromium >nul

echo [INFO] Iniciando automacao...
"%VENV_PY%" "%SCRIPT%"

pause
exit /b 0
