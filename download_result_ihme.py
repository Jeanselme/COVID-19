import os
import requests, zipfile, io
from us import states
import numpy as np
import pandas as pd
import argparse

# Parse input / ouput
parser = argparse.ArgumentParser()
parser.add_argument('-o', '--output', help="Output Path", default ='results')
parser.add_argument('-l', '--last', help="Download only last", action='store_true')
args = parser.parse_args()

if not os.path.isdir(os.path.join(args.output, 'ihme')):
    os.mkdir(os.path.join(args.output, 'ihme'))

def fromStateToAbbr(state):
    search = states.lookup(state)
    if search is not None:
        return search.abbr
    else:
        return np.nan

# Download urls
urls = ['https://ihmecovid19storage.blob.core.windows.net/latest/ihme-covid19.zip']

# Add previous urls
if not args.last:
    urls += ["https://ihmecovid19storage.blob.core.windows.net/archive/{:%Y-%m-%d}/ihme-covid19.zip".format(d) for d in pd.date_range(start='2020-03-28', end=pd.Timestamp('today'))]

for url in urls:
    print('Download from {}'.format(url))
    try:
        r = requests.get(url)
        z = zipfile.ZipFile(io.BytesIO(r.content))

        csv_path = [i.filename for i in z.filelist if '.csv' in i.filename][0]

    
        date = csv_path.split('/')[0].split('.')[0].replace('_', '') 

        # Parse to have similar format
        ihme_predictions = pd.read_csv(z.open(csv_path), parse_dates=True)
        ihme_predictions['date'] = ihme_predictions[[c for c in ihme_predictions.columns if 'date' in c][0]] # Change name in some version 
        ihme_predictions['state'] = ihme_predictions[[c for c in ihme_predictions.columns if 'location' in c][0]].apply(fromStateToAbbr) # Change name in some version
        ihme_predictions['pred_deaths'] = ihme_predictions['deaths_mean']
        ihme_predictions['pred_hosp'] = ihme_predictions['allbed_mean']
        ihme_predictions = ihme_predictions[['state', 'date', 'pred_hosp', 'pred_deaths']].dropna()

        # Save per state
        for state in ihme_predictions.state.unique():
            ihme_predictions[ihme_predictions.state == state][['date', 'pred_deaths', 'pred_hosp']].to_csv(os.path.join(args.output, 'ihme', '{}_{}.csv'.format(state, date)), index = False)

    except Exception as e:
        print("Format has changed")
        print(e)