import os
import logging
import requests
from pymongo import MongoClient
from utils import chunks
from joblib import Parallel, delayed
import tqdm
import zipfile
import tarfile

client = MongoClient("mongodb://localhost:27017/")
package= client["license"]["package"]
WHEEL_DIR = "data/pkg_wheels"

def open_wheel(package: str,versions:list):
    requires_lst=[]
    requires_lst.append(f"https://pypi.org/pypi/{package}/json")
    while len(requires_lst) > 0:
        url = requires_lst.pop(0)
        try:
            r = requests.get(url)
            if r.status_code == 404:
                logging.error(f"{package} does not exist on PyPI")
                return 0
            pypi_info=r.json()
        except Exception as e:
            logging.error(f"query {package} Release error! {e}")
            requires_lst.append(url)
        
    for version in versions:   
        try:
            file_infos = pypi_info['releases'][version]
        except:
            logging.error(f"{package} {version} does not exist on PyPI")
            continue
            
        for whl_file in file_infos:
            if whl_file is not None:
                store_path = os.path.join(WHEEL_DIR, whl_file['filename'])
                if os.path.exists(store_path):
                    try:
                        if store_path.endswith("zip") or store_path.endswith("whl") or store_path.endswith("egg"):
                            zfile=zipfile.ZipFile(store_path)
                            names=zfile.namelist()
                            licenses=list(filter(lambda e: "license" in e.lower() and not zfile.getinfo(e).is_dir(),names))
                            if licenses:
                                license=licenses[0]
                                if not os.path.exists(f"data/license/{package}/{version}/"):
                                    os.makedirs(f"data/license/{package}/{version}/")
                                if not os.path.exists(f"data/license/{package}/{version}/{license}"):
                                    zfile.extract(license,f"data/license/{package}/{version}/")
                            readmes=list(filter(lambda e: "readme" in e.lower() and not zfile.getinfo(e).is_dir(),names))
                            if readmes:
                                readme=readmes[0]
                                if not os.path.exists(f"data/license/{package}/{version}/"):
                                    os.makedirs(f"data/license/{package}/{version}/")
                                if not os.path.exists(f"data/license/{package}/{version}/{readme}"):
                                    zfile.extract(readme,f"data/license/{package}/{version}/")
                            break
                        elif store_path.endswith("tar.gz") or store_path.endswith("tar"):
                            tfile=tarfile.open(store_path)
                            names=tfile.getnames()
                            licenses=list(filter(lambda e: "license" in e.lower() and tfile.getmember(e).isfile(),names))
                            if licenses:
                                license=licenses[0]
                                if not os.path.exists(f"data/license/{package}/{version}/"):
                                    os.makedirs(f"data/license/{package}/{version}/")
                                if not os.path.exists(f"data/license/{package}/{version}/{license}"):
                                    tfile.extract(license,f"data/license/{package}/{version}/")
                            readmes=list(filter(lambda e: "readme" in e.lower() and tfile.getmember(e).isfile(),names))
                            if readmes:
                                readme=readmes[0]
                                if not os.path.exists(f"data/license/{package}/{version}/"):
                                    os.makedirs(f"data/license/{package}/{version}/")
                                if not os.path.exists(f"data/license/{package}/{version}/{readme}"):
                                    tfile.extract(readme,f"data/license/{package}/{version}/")
                            break
                    except Exception as e:
                        logging.error(e)
                        

                    
                        
                        
                    
                               
def main(lst,log_i):
    logging.basicConfig(
        filename=f"log/download{log_i}.log",
        filemode='w',
        format="%(asctime)s (Process %(process)d) [%(levelname)s] %(message)s",
        level=logging.INFO
    )
    for i in lst:
        pkg=i["name"]
        versions=i["version"]
        open_wheel(pkg,versions)
        
if __name__ =="__main__":      
    no_license = package.find({"license_clean":"Unrecognizable" })

    chunk_lst=chunks(list(no_license),50)
    Parallel(n_jobs=50)(delayed(main)(task,i%40) for i,task in tqdm.tqdm(enumerate(chunk_lst),total=len(no_license)/50))                                             
                        
