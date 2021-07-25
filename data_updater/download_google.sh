git pull --rebase

python3 ./data_updater/download_google.py

git add ./dashApp/data/google_mobility_australia.csv
git add ./dashApp/data/google_data.txt
git commit -am "Updating Google Data for App"
git push
