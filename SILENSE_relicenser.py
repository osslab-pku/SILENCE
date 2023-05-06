import logging
import argparse
import traceback
import pandas as pd
import multiprocessing as mp

from typing import List, Dict
from collections import Counter
from pymongo import MongoClient
from analysis import is_compatible, get_license_data


logger = logging.getLogger(__name__)
TOP_LICENSES: Dict[str, int] = Counter(
    get_license_data(sample=True, n_jobs=20)[0].license
)
LICENSE_TERMS: pd.DataFrame = pd.read_csv("knowledge_base/terms.csv")
ALL_LICENSES: list = LICENSE_TERMS["license"].tolist()

def get_compatible_licenses(mongo_uri: str, package: str, version: str) -> List[str]:
    client = MongoClient(mongo_uri, tz_aware=True)
    package_db = client["license"]["package"]
    sample = package_db.find_one({"name": package, "version": version})

    deps = [(n["name"], n["version"]) for n in sample["tree_created"]]
    all_licenses = set()
    for pkg, ver in deps:
        doc = package_db.find_one({"name": pkg.lower(), "version": ver})
        all_licenses.add(doc["license_clean"])

    compatible_licenses = []
    for license, _ in sorted(TOP_LICENSES.items(), key=lambda x: -x[1]):
        if license not in ALL_LICENSES:
            continue
        if license == "Unrecognizable":
            continue
        if all(is_compatible(a, license) != "Incompatible" for a in all_licenses):
            compatible_licenses.append(license)
        if len(compatible_licenses) >= 10:
            break

    client.close()
    return compatible_licenses


def get_compat_licenses_worker(mongo_uri: str, pkg: str, ver: str) -> dict:
    try:
        logger.info("Get compatible license for %s %s", pkg, ver)
        return {
            "package": pkg,
            "version": ver,
            "compatible_licenses": get_compatible_licenses(mongo_uri, pkg, ver),
        }
    except Exception as ex:
        logger.error("%s %s: %s\n%s", pkg, ver, ex, traceback.format_exc())
        return {"package": pkg, "version": ver, "error": str(ex)}


def get_compatible_licenses_all(mongo_uri: str):
    incompats = pd.read_csv("res/license_incompatibilities.csv")
    incompat_set = set(zip(incompats.package, incompats.version))
    params = [(mongo_uri, pkg, ver) for pkg, ver in incompat_set]
    with mp.Pool(mp.cpu_count() // 2) as pool:
        result = pool.starmap(get_compat_licenses_worker, params)
    result = pd.DataFrame(result).sort_values(by=["package", "version"])
    result.to_csv("res/relicensing.csv", index=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("scope", choices=["one", "all"])
    parser.add_argument("-n", "--name", type=str, required=False)
    parser.add_argument("-v", "--version", type=str, required=False)
    parser.add_argument(
        "--mongo_uri", type=str, required=False, default="mongodb://localhost:27017/"
    )

    args = parser.parse_args()

    logging.basicConfig(
        format="%(asctime)s (Process %(process)d) [%(levelname)s] %(filename)s:%(lineno)d %(message)s",
        level=logging.INFO if args.scope == "all" else logging.DEBUG,
    )

    if args.scope == "one":
        compats = get_compatible_licenses(args.mongo_uri, args.name, args.version)
        logger.info("Top 10 Compatible Licenses: %s", compats)
    else:
        get_compatible_licenses_all(args.mongo_uri)


if __name__ == "__main__":
    main()
