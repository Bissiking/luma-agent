@echo off
chcp 65001 >nul
REM =============================
REM  LUMA ORION AGENT – Setup
REM  Auteur : M. HEMERY
REM =============================

setlocal

echo [LUMA-Agent] 🔍 Préparation...

REM --- Dossier agent (dossier du script) ---
set AGENT_PATH=%~dp0
set AGENT_PATH=%AGENT_PATH:~0,-1%
set VENV_PATH=%AGENT_PATH%\venv

cd /d "%AGENT_PATH%"

REM --- Vérification Python ---
where python >nul 2>&1
if errorlevel 1 (
    echo [LUMA-Agent] ❌ Python non trouvé
    exit /b 1
)

REM --- Venv ---
if not exist "%VENV_PATH%" (
    echo [LUMA-Agent] 🧪 Création du venv...
    python -m venv venv
)

REM --- Dépendances ---
echo [LUMA-Agent] 📦 Installation des dépendances...
"%VENV_PATH%\Scripts\python.exe" -m pip install --upgrade pip
"%VENV_PATH%\Scripts\pip.exe" install -r requirements.txt

REM --- Lancement ---
echo [LUMA-Agent] 🚀 Lancement de l'agent Orion...
"%VENV_PATH%\Scripts\python.exe" agent.py

endlocal
