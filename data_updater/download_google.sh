git -C /home/tobin/CovidMobilityApp pull --rebase

python /home/tobin/CovidMobilityApp /data_updater/download_google.py

git -C /home/tobin/CovidMobilityApp add /home/tobin/CovidMobilityApp/dashApp/data/google_mobility_australia.csv
git -C /home/tobin/CovidMobilityApp add /home/tobin/CovidMobilityApp/dashApp/data/google_data.txt
git -C /home/tobin/CovidMobilityApp commit -am "Updating Google Data for App"
git -C /home/tobin/CovidMobilityApp push
