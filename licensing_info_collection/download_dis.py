import os

import time
import logging
import requests
from pymongo import MongoClient

import multiprocessing as mp
import random
from utils import chunks
from joblib import Parallel, delayed
import tqdm

client = MongoClient("mongodb://localhost:27017/")
package= client["license"]["package"]
WHEEL_DIR = "data/pkg_wheels"


def download_wheel(package: str,versions:list):
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
                    
                    logging.info(f"{whl_file['filename']} already exists")
                    break
                else:
                    logging.info(f"Downloading {whl_file['filename']} ")
                    try:
                        with requests.get(whl_file['url'], allow_redirects=True) as r:
                            open(store_path, 'wb').write(r.content)
                        #wget.download(url=whl_file['url'],out=store_path)
                        time.sleep(0.3+0.1 * random.randint(0, 12))
                        logging.info(f"Finish {whl_file['filename']}")
                        break
                    except Exception as e:
                        logging.error(f"download {whl_file['filename']} error! {e}")
                        pass
        
                        
                
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
        download_wheel(pkg,versions)
        
if __name__ == "__main__":       
    no_license = package.find({"license_clean":"Unrecognizable" })

    chunk_lst=chunks(list(no_license),50)
    Parallel(n_jobs=50)(delayed(main)(task,i%40) for i,task in tqdm.tqdm(enumerate(chunk_lst),total=len(no_license)/50))


