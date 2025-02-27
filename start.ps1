# Script de démarrage pour Windows PowerShell
$ErrorActionPreference = "Stop"

function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

function Check-Command($cmdname) {
    return [bool](Get-Command -Name $cmdname -ErrorAction SilentlyContinue)
}

# Vérifier si Python est installé
if (-not (Check-Command python)) {
    Write-ColorOutput Red "Python n'est pas installé. Veuillez installer Python 3.8 ou supérieur."
    exit 1
}

# Vérifier la version de Python
$pythonVersion = (python --version 2>&1).ToString().Split(" ")[1]
$minVersion = [version]"3.8"
if ([version]$pythonVersion -lt $minVersion) {
    Write-ColorOutput Red "Python $pythonVersion détecté. Version 3.8 ou supérieure requise."
    exit 1
}

Write-ColorOutput Green "Python $pythonVersion détecté"

# Créer et activer l'environnement virtuel si nécessaire
if (-not (Test-Path "venv")) {
    Write-ColorOutput Yellow "Création de l'environnement virtuel..."
    python -m venv venv
}

# Activer l'environnement virtuel
Write-ColorOutput Yellow "Activation de l'environnement virtuel..."
& .\venv\Scripts\Activate.ps1

# Installer/mettre à jour les dépendances
Write-ColorOutput Yellow "Installation/mise à jour des dépendances..."
python -m pip install --upgrade pip
pip install -r requirements.txt

# Vérifier si le fichier .env existe
if (-not (Test-Path ".env")) {
    Write-ColorOutput Yellow "Création du fichier .env depuis .env.example..."
    Copy-Item .env.example .env
    Write-ColorOutput Yellow "Veuillez configurer le fichier .env avec vos paramètres."
}

# Lancer l'agent
Write-ColorOutput Green "Démarrage de LUMA Agent..."
python main.py 