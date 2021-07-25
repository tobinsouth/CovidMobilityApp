git pull --rebase

module load arch/haswell
module load Python/3.6.1-foss-2016b
source ../virtualenvs/bin/activate

python3 ./data_updater/download_google.py

deactivate

git add ./dashApp/data/google_mobility_australia.csv
git add ./dashApp/data/google_data.txt
git commit -am "Updating Google Data for App"
git push