#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Point d'entrée pour l'agent de monitoring P-2.0.0-Grizzly
"""

import os
import sys

# Ajouter le répertoire parent au chemin d'importation
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Importer le module principal
from src.agent import main

if __name__ == "__main__":
    main() 