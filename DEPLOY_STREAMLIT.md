# Déployer InternMatch sur Streamlit Community Cloud

Cette édition est une application Streamlit autonome : elle expose les offres web vérifiées, la recherche, les favoris de session, le profil, les statistiques et une carte. Elle peut lire la même base MySQL que le backend FastAPI lorsque les secrets MySQL sont renseignés.

## 1. Envoyer le projet sur GitHub

Crée un dépôt GitHub privé ou public, puis envoie le dossier `InternMatch-main`. Le fichier `.gitignore` exclut les fichiers `.env`, les secrets Streamlit, les clés, les environnements Python et les fichiers temporaires. Vérifie tout de même les fichiers affichés par GitHub avant le premier envoi.

## 2. Créer l’application Cloud

1. Ouvre [share.streamlit.io](https://share.streamlit.io/).
2. Choisis **Create app** puis ton dépôt GitHub.
3. Sélectionne la branche à publier.
4. Dans **Main file path**, indique `streamlit_app.py`.
5. Clique sur **Deploy**.

Streamlit installe automatiquement les dépendances de `requirements.txt`.

## 3. Vérifier le déploiement

Après le message **Your app is live**, ouvre l’URL fournie par Streamlit puis vérifie :

1. La page d’accueil affiche le bandeau *Trouvez votre stage idéal à Marrakech*.
2. La recherche par type, ville, filière et mot-clé filtre les offres.
3. Le bouton ♡ ajoute une offre aux favoris pour la session en cours.
4. Les boutons des offres ouvrent leur site source dans un nouvel onglet.
5. Sans secrets MySQL, le message *Mode web autonome* apparaît et l’application reste fonctionnelle.

## 4. Connecter MySQL (optionnel)

Une base MySQL sur `localhost` ne peut pas être atteinte depuis Streamlit Cloud. Utilise une base MySQL gérée et accessible depuis Internet, avec un utilisateur applicatif limité. Dans l’application Streamlit, ouvre **Settings → Secrets** puis colle :

```toml
[mysql]
host = "your-public-mysql-host"
port = 3306
database = "internmatch_db"
user = "internmatch_app"
password = "replace-with-a-strong-password"
```

Relance ensuite l’application. Sans ces secrets, l’application reste fonctionnelle avec les offres web, sans afficher les données MySQL.

## Limites à connaître

- Les favoris et le profil restent dans la session Streamlit et ne deviennent pas un compte utilisateur.
- Cette édition Streamlit ne reçoit et ne stocke aucun CV. Pour recevoir réellement des candidatures, déploie l’API FastAPI avec un stockage de fichiers privé et persistant, puis relie un formulaire sécurisé à cette API.
- Les liens d’offres ouvrent toujours leurs sites sources : leur disponibilité doit être vérifiée avant de postuler.
