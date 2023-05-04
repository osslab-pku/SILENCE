from pymongo import MongoClient
from joblib import Parallel, delayed
from utils import chunks
import tqdm
import json

client = MongoClient("mongodb://localhost:27017/")
release= client["pypi"]["release_metadata"]
package= client["license"]["package"]


dirty2clean=json.load(open("res/dirty2clean.json","r"))
keyword=json.load(open("knowledge_base/keywords.json","r"))
def have_keywords(dirty,clean,ver=False):
    dirty=dirty.lower()
    if clean not in keyword:
        return False
    req=keyword[clean]

    if "name" in req:
        if len(list(filter(lambda e:e in dirty,req["name"]))) == 0:
            return False
    if "must" in req:
        if len(list(filter(lambda e:e in dirty,req["must"]))) == 0:
            return False
    if "no" in  req:
        if len(list(filter(lambda e:e in dirty,req["no"]))) != 0:
            return False
    if ver and "version" in req:
        if len(list(filter(lambda e:e in dirty,req["version"]))) == 0:
            return False
    return True

def find_license_by_keywords(dirty):
    for clean in keyword:
        if have_keywords(dirty,clean,True):
            return clean
    return None


def main(lst):
    for name in lst:
        for i in package.find({"name":name,"license":{"$ne":None}}):
            version=i["version"]
            dirty=i["license"].lower()
            if dirty in ["null","unknown","none"]:
                package.update_one({"name":name,"version":version},{"$set":{"license_clean":"Unrecognizable"}})
                continue
            if dirty in dirty2clean:
                max_possibility_license=sorted(dirty2clean[dirty].items(),key=lambda e:-e[1])[0][0]
                res=package.find_one({"name":name,"version":version})
                if "license_classifier" in res and max_possibility_license == res["license_classifier"]:
                    package.update_one({"name":name,"version":version},{"$set":{"license_clean":max_possibility_license}})
                    continue
                if have_keywords(dirty,max_possibility_license):
                    package.update_one({"name":name,"version":version},{"$set":{"license_clean":max_possibility_license}})
                else:
                    max_possibility_license=find_license_by_keywords(dirty)
                    if max_possibility_license:
                        package.update_one({"name":name,"version":version},{"$set":{"license_clean":max_possibility_license}})
                    else:
                        package.update_one({"name":name,"version":version},{"$set":{"license_clean":"Unrecognizable"}})
            else:
                max_possibility_license=find_license_by_keywords(dirty)
                if max_possibility_license:
                    package.update_one({"name":name,"version":version},{"$set":{"license_clean":max_possibility_license}})
                else:
                    package.update_one({"name":name,"version":version},{"$set":{"license_clean":"Unrecognizable"}})

    

if __name__ == "__main__":
    count=package.count_documents({"license":{"$ne":None}})
    print(count)
    
    names=package.distinct("name")
    chunk_lst=chunks(list(names),50)
    Parallel(n_jobs=120,require='sharedmem')(delayed(main)(task) for task in tqdm.tqdm(chunk_lst,total=len(names)/50))

    
