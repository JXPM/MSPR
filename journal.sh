# Créer un nouveau dépôt GitHub 
git init
git branch -M main
git add .
git commit -m "first commit"
gh repo create MSPR --private
git remote add origin https://github.com/JXPM/MSPR.git
git push --set-upstream origin main

# Créer un environnement virtuel et installer les dépendances
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# lancer le serveur de développement
uvicorn app.main:app --reload


#fichier Maj et push
git status
git add journal.sh
git commit -m "maj Readme"
git push origin main

# pull  
git pull origin main

# switch branch
git checkout  joseph

git branch
git status
git add .
git commit -m "Maj MCD et ajout latex"
git push --set-upstream origin joseph  


# merge branch
git checkout main