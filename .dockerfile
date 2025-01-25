# Utiliser une image de base Alpine
FROM alpine:latest

# Définir une variable d'environnement par défaut pour l'URL de l'API
ENV API_URL=https://mhemery.fr

# Mettre à jour et installer les dépendances nécessaires
RUN apk update && apk add --no-cache \
    git \
    nodejs \
    npm

# Cloner le dépôt Git avec la branche spécifiée
RUN git clone https://github.com/Bissiking/luma-agent.git --branch agent-v2-light /app

# Configurer le répertoire de travail
WORKDIR /app

# Installer les dépendances Node.js
RUN npm install

# Exposer le port utilisé par l'application
EXPOSE 3000

# Commande pour démarrer l'application
CMD ["npm", "start"]
