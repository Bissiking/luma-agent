# Utiliser une image de base officielle Node.js à partir de Docker Hub
FROM node:14

# Définir le répertoire de travail à l'intérieur du conteneur
WORKDIR /app

# Installation de GIT
RUN apt-get update && apt-get install -y git

# Cloner le dépôt GitHub
RUN git clone https://github.com/Bissiking/luma-agent.git --branch agent-v2-light .

# Installer les dépendances du projet
RUN npm install

# Définir la commande de démarrage de l'application
CMD ["npm", "start"]
