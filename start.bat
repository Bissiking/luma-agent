@echo off
setlocal enabledelayedexpansion

:: Couleurs pour Windows
set "RED=41"
set "GREEN=42"
set "YELLOW=43"

:: Fonction pour afficher du texte en couleur
:colorEcho
echo [%~1m%~2[0m
exit /b

:: Vérifier si Python est installé
python --version > nul 2>&1
if errorlevel 1 (
    call :colorEcho %RED% "Python n'est pas installe. Veuillez installer Python 3.8 ou superieur."
    exit /b 1
)

:: Vérifier la version de Python
for /f "tokens=2" %%I in ('python --version 2^>^&1') do set "PYTHON_VERSION=%%I"
echo Version Python detectee: %PYTHON_VERSION%

:: Supprimer l'ancien environnement virtuel s'il existe
if exist "venv" (
    call :colorEcho %YELLOW% "Suppression de l'ancien environnement virtuel..."
    rmdir /s /q venv
)

:: Créer un nouvel environnement virtuel
call :colorEcho %YELLOW% "Creation de l'environnement virtuel..."
python -m venv venv

:: Activer l'environnement virtuel
call :colorEcho %YELLOW% "Activation de l'environnement virtuel..."
call venv\Scripts\activate.bat

:: Installer/réparer pip
call :colorEcho %YELLOW% "Installation/reparation de pip..."
curl -o get-pip.py https://bootstrap.pypa.io/get-pip.py
python get-pip.py --force-reinstall
del get-pip.py

:: Installer les dépendances
call :colorEcho %YELLOW% "Installation des dependances..."
python -m pip install -r requirements.txt

:: Vérifier si le fichier .env existe
if not exist ".env" (
    call :colorEcho %YELLOW% "Creation du fichier .env depuis .env.example..."
    copy .env.example .env
    call :colorEcho %YELLOW% "Veuillez configurer le fichier .env avec vos parametres."
)

:: Lancer l'agent
call :colorEcho %GREEN% "Demarrage de LUMA Agent..."
python main.py

endlocal 