from pymongo import MongoClient
import tqdm
import json
import pandas as pd
from collections import defaultdict
client = MongoClient("mongodb://localhost:27017/")

package= client["license"]["package"]


df2 = pd.read_csv("knowledge_base/terms.csv")
license_lst=df2['license'].tolist()




#print(len(license_lst))
clean2dirty=defaultdict(dict)
dirty2clean=defaultdict(dict)
 
for clean in tqdm.tqdm(license_lst):
    for i in package.find({"license_classifier":clean}):
        if i["license"]:
            clean2dirty[clean][i["license"].lower()]=clean2dirty[clean].get(i["license"].lower(),0)+1
            dirty2clean[i["license"].lower()][clean]=dirty2clean[i["license"].lower()].get(clean,0)+1


json.dump(clean2dirty,open("res/clean2dirty.json","w"))
json.dump(dirty2clean,open("res/dirty2clean.json","w"))
