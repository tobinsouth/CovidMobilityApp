git pull --rebase

/home/a1171654/python3/Python-3.7.0/python ./data_updater/download_google.py

git add ./dashApp/data/google_mobility_australia.csv
git add ./dashApp/data/google_data.txt
git commit -am "Updating Google Data for App"
git push
