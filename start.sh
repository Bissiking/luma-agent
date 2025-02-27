#!/bin/bash

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fonction pour afficher des messages en couleur
print_color() {
    color=$1
    message=$2
    echo -e "${color}${message}${NC}"
}

# Vérifier si Python est installé
if ! command -v python3 &> /dev/null; then
    print_color "$RED" "Python n'est pas installé. Veuillez installer Python 3.8 ou supérieur."
    exit 1
fi

# Vérifier la version de Python
PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
MIN_VERSION="3.8.0"

if [ "$(printf '%s\n' "$MIN_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$MIN_VERSION" ]; then
    print_color "$RED" "Python $PYTHON_VERSION détecté. Version 3.8 ou supérieure requise."
    exit 1
fi

print_color "$GREEN" "Python $PYTHON_VERSION détecté"

# Supprimer l'ancien environnement virtuel s'il existe
if [ -d "venv" ]; then
    print_color "$YELLOW" "Suppression de l'ancien environnement virtuel..."
    rm -rf venv
fi

# Créer un nouvel environnement virtuel
print_color "$YELLOW" "Création de l'environnement virtuel..."
python3 -m venv venv

# Activer l'environnement virtuel
print_color "$YELLOW" "Activation de l'environnement virtuel..."
source venv/bin/activate

# Installer/réparer pip
print_color "$YELLOW" "Installation/réparation de pip..."
curl -o get-pip.py https://bootstrap.pypa.io/get-pip.py
python get-pip.py --force-reinstall
rm get-pip.py

# Installer les dépendances
print_color "$YELLOW" "Installation des dépendances..."
python -m pip install -r requirements.txt

# Vérifier si le fichier .env existe
if [ ! -f ".env" ]; then
    print_color "$YELLOW" "Création du fichier .env depuis .env.example..."
    cp .env.example .env
    print_color "$YELLOW" "Veuillez configurer le fichier .env avec vos paramètres."
fi

# Lancer l'agent
print_color "$GREEN" "Démarrage de LUMA Agent..."
python main.py 