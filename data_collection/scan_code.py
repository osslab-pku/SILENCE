import subprocess
import json
import os
from utils import chunks
from joblib import Parallel, delayed
import tqdm
from pymongo import MongoClient
import pandas as pd
client = MongoClient("mongodb://localhost:27017/")
release= client["pypi"]["release_metadata"]
package= client["license"]["package"]

def license_detection_files(file_path,output_path,pkg):
    results={}
    pipe = subprocess.Popen(
        ["scancode","-l" ,"-n","4","--license-score","95","--json", output_path, file_path,"--license-text"],#relative path
        stdout=subprocess.PIPE)
    return_code=pipe.wait()
    with open(output_path,"r") as f:
        res=json.load(f)
        files=res["files"]
        for file in files:
            licenses=file["licenses"]
            if licenses:
                licenses.sort(key=lambda e: - e["score"])
                licenses_spdx=[]
                for license in licenses:
                    if "scancode" not in license["spdx_license_key"]:
                        licenses_spdx.append(license["spdx_license_key"])
                results[file["path"]]=list(set(licenses_spdx))
    # dep_license=get_dependencies_licenses(file_path)
    # results.update(dep_license)
    json.dump(results,open(f"/data/license_res/{pkg}.json","w"))
    return results

def main(lst):
    for i in lst:
        license_detection_files(f"/data/license/{i}",f"/data/license_res/{i}_res.json",i)


def get_license_type(license: str) -> str:
    df = pd.read_csv("knowledge_base/terms.csv")
    license_terms = df[df['license'] == license].to_dict(orient='records')
    if license_terms:
        license_terms=license_terms[0]
        copyleft=license_terms["copyleft"]
        return copyleft    
    else:
        return -1
if __name__ == "__main__":
    pkgs=os.listdir("/data/license")

    chunk_lst=chunks(pkgs,50)
    Parallel(n_jobs=40)(delayed(main)(task) for i,task in tqdm.tqdm(enumerate(chunk_lst),total=len(pkgs)/50))

    pkgs=os.listdir("/data/license")
    dic={}
    for pkg in tqdm.tqdm(pkgs):
        f=json.load(open(f"/data/license_res/{pkg}.json","r"))
        dic.update(f)
    #json.dump(dic,open("res/pkg_license.json","w"))
    
    
    res={}
    for key in tqdm.tqdm(dic):
        if dic[key]:
            lst=key.split("/")
            name=lst[0]
            version=lst[1]
            
            tmp=res.get(name,{})
            if "license" in key.lower():
                tmpv=tmp.get(version,{})
                tmpv["license"]=dic[key]
                tmp[version]=tmpv
            else:
                tmpv=tmp.get(version,{})
                tmpv["readme"]=dic[key]
                tmp[version]=tmpv
            res[name]=tmp
    
    json.dump(res,open("res/pkg_license_res.json","w"))
        #package.update_one({"name":name,"version":version},{"$set":{"license_clean":dic[key]}})
        
    for pkg in tqdm.tqdm(res):
        releases=res[pkg]
        for version in releases:
            release=releases[version]
            if "license" in release:
                li=sorted(release["license"],key=lambda e: -get_license_type(e))[0]
            else:
                li=sorted(release["readme"],key=lambda e: -get_license_type(e))[0]
            package.update_one({"name":pkg,"version":version},{"$set":{"license_clean":li}})
                
        
    