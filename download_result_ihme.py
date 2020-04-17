import requests, zipfile, io
from us import states
import numpy as np
import pandas as pd
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-o', '--output', help="Output Path", default ='results')
args = parser.parse_args()

def fromStateToAbbr(state):
    search = states.lookup(state)
    if search is not None:
        return search.abbr
    else:
        return np.nan

download_last = True # Download only the last if True
urls = ['https://ihmecovid19storage.blob.core.windows.net/latest/ihme-covid19.zip']

if not download_last:
    urls += ["https://ihmecovid19storage.blob.core.windows.net/archive/{:%Y-%m-%d}/ihme-covid19.zip".format(d) for d in pd.date_range(start='2020-03-28', end='2020-04-10')]

for url in urls:
    print('Download from {}'.format(url))
    try:
        r = requests.get(url)
        z = zipfile.ZipFile(io.BytesIO(r.content))

        csv_path = [i.filename for i in z.filelist if '.csv' in i.filename][0]

    
        date = csv_path.split('/')[0].split('.')[0].replace('_', '') 
        ihme_predictions = pd.read_csv(z.open(csv_path), parse_dates=True)
        ihme_predictions['date'] = ihme_predictions[[c for c in ihme_predictions.columns if 'date' in c][0]] # Change name in some version 
        ihme_predictions['state'] = ihme_predictions[[c for c in ihme_predictions.columns if 'location' in c][0]].apply(fromStateToAbbr) # Change name in some version
        ihme_predictions['pred_deaths'] = ihme_predictions['deaths_mean']
        ihme_predictions['pred_hosp'] = ihme_predictions['allbed_mean']
        ihme_predictions = ihme_predictions[['state', 'date', 'pred_hosp', 'pred_deaths']].dropna()

        for state in ihme_predictions.state.unique():
            ihme_predictions[ihme_predictions.state == state][['date', 'pred_deaths', 'pred_hosp']].to_csv(os.path.join(args.output, 'ihme', '{}_{}.csv'.format(state, date)), index = False)

    except Exception as e:
        print("Format has changed")
        print(e)