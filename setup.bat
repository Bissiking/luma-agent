@echo off
REM =============================
REM  LUMA ORION AGENT – Setup
REM  Auteur : M. HEMERY
REM =============================

setlocal ENABLEDELAYEDEXPANSION

echo [LUMA-Agent] 🔍 Préparation...

REM --- Vérification Python ---
where python >nul 2>&1
if errorlevel 1 (
    echo [LUMA-Agent] ❌ Python non trouvé. Installe Python 3.10+ et relance.
    exit /b 1
)

echo [LUMA-Agent] 🐍 Python détecté

REM --- Dossier agent ---
set AGENT_PATH=C:\luma-agent
set VENV_PATH=%AGENT_PATH%\venv

if not exist "%AGENT_PATH%" (
    mkdir "%AGENT_PATH%"
)

cd /d "%AGENT_PATH%"

REM --- Venv ---
if not exist "%VENV_PATH%" (
    echo [LUMA-Agent] 🧪 Création de l'environnement virtuel...
    python -m venv venv
)

REM --- Activation ---
echo [LUMA-Agent] ⚙️ Activation du venv...
call "%VENV_PATH%\Scripts\activate.bat"

REM --- Dépendances Python ---
echo [LUMA-Agent] 📦 Installation des dépendances Python...
python -m pip install --upgrade pip
pip install requests psutil
pip install -r requirements.txt

REM --- Lancement ---
echo [LUMA-Agent] 🚀 Lancement de l'agent Orion...
python agent.py

endlocal
