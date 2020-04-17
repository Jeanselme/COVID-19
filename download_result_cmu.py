import os
import pandas as pd
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input', help="Output Path", default ='input')
parser.add_argument('-o', '--output', help="Output Path", default ='results')
args = parser.parse_args()

if not os.path.isdir(os.path.join(args.output, 'bayes_sir')):
    os.mkdir(os.path.join(args.output, 'bayes_sir'))

for d in os.listdir(args.input):
    path_d = os.path.join(args.input, d)
    if os.path.isdir(path_d):
        for f in os.listdir(path_d):
            path_f = os.path.join(path_d, f)
            if 'all' not in f and '.csv' in f:
                date = d[:d.index('_')].replace('-', '')
                state = f[:f.index('.csv')]
                state_data = pd.read_csv(path_f, parse_dates=['date'])[['date', 'deaths', 'cases', 'hospitalizations']]
                state_data = state_data.rename(columns={"deaths": "pred_deaths", "cases": "pred_cases", "hospitalizations": "pred_hosp"})
                state_data.to_csv(os.path.join(args.output, 'bayes_sir', '{}_{}.csv'.format(state, date)), index = False)