import pymongo
import multiprocessing as mp

from dateutil.parser import parse
from pymongo import MongoClient


def store_dep_graph(pkg_name):
    print(f"Processing {pkg_name}...")

    client = MongoClient("mongodb://localhost:27017/", tz_aware=True)
    dist_db = client["pypi"]["distribution_metadata"]
    package_db = client["license"]["package"]

    for metadata in dist_db.find({"name": pkg_name}):
        key = {"name": metadata["name"].lower(), "version": metadata["version"]}
        if package_db.count_documents(key) > 0:
            full = package_db.find_one(key)
            # Sometimes only a few entries have requires_dist information
            if len(full["requires_dist"]) == 0:
                full["requires_dist"] = metadata["requires_dist"]
        else:
            full = {
                **key,
                "release_date": parse(metadata["upload_time"]),
                "license": metadata["license"] if "license" in metadata else None,
                "requires_dist": metadata["requires_dist"],
            }
        package_db.replace_one(key, full, upsert=True)

    client.close()


def main():
    client = MongoClient("mongodb://localhost:27017/", tz_aware=True)
    dist_db = client["pypi"]["distribution_metadata"]
    package_db = client["license"]["package"]
    package_db.create_index(
        [("name", pymongo.ASCENDING), ("version", pymongo.ASCENDING)], unique=True
    )
    with mp.Pool(mp.cpu_count()) as p:
        p.map(store_dep_graph, dist_db.distinct("name"))
    client.close()


if __name__ == "__main__":
    main()
