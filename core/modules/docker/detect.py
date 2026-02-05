# ============================================================
# Orion Agent — Docker detection
# Auteur : M. HEMERY
# ============================================================

import shutil
import subprocess


def docker_available():
    """Vérifie si Docker est installé et accessible."""
    if not shutil.which("docker"):
        return False

    try:
        subprocess.check_output(
            ["docker", "info"],
            stderr=subprocess.DEVNULL,
            timeout=3
        )
        return True
    except Exception:
        return False
