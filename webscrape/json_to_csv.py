import pandas as pd
import glob
import json
import csv
from csv import  writer


DATA_PATH = 'D:/GCPLP_practice_module/data/data*.json'

json_files = glob.glob(DATA_PATH)

data = []

filename = 'allrecipies.csv'

for jf in json_files:
    with open(jf, 'r', encoding = 'utf-8') as f:
        json_file = json.load(f)
        data.append([json_file['title'], json_file['instructions'], json_file['ingredients']])


df = pd.DataFrame(data, columns=['title', 'instructions', 'ingredients'])
df.to_csv(filename, sep=',', encoding='utf-8', index = False)

