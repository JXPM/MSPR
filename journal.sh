# Créer un nouveau dépôt GitHub 
git init
git branch -M main
git add .
git commit -m "first commit"
gh repo create MSPR --private
git remote add origin https://github.com/JXPM/MSPR.git
git push --set-upstream origin main



#fichier Maj et push
git status
git add journal.sh
git commit -m "maj journal.sh"
git push origin main

# pull  
git pull origin main --rebase

# switch branch
git checkout -b api 

git branch
git status
git add .
git commit -m "Initialisation du backend FastAPI structure"
git push --set-upstream origin api


# merge branch
git checkout main
git merge api