# roadef
# Mettre main à jour
git checkout main
git pull --rebase origin main

# Créer une branche de travail
git checkout -b feat/nom-feature-prenom
git push -u origin feat/nom-feature-prenom

# Travailler
git status
git add <fichiers>
git commit -m "Message clair"
git push

# Mettre à jour ta branche après changement sur main
git checkout main
git pull --rebase origin main
git checkout feat/nom-feature-prenom
git rebase main
git push --force-with-lease