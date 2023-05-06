import logging
import multiprocessing as mp

from datetime import datetime, timezone
from dep_resolve.resolver import DependencyResolver
from pymongo import MongoClient


MONGO_URL = "mongodb://localhost:27017/"


def build_dep_trees(pkg: str):
    client = MongoClient(MONGO_URL, tz_aware=True)
    package_db = client["license"]["package"]
    query = {"name": pkg.lower(), "tree_created": {"$exists": False}}
    resolver = DependencyResolver(MONGO_URL)

    for pkg_data in package_db.find(query):
        key = {"name": pkg.lower(), "version": pkg_data["version"]}
        pkg_data = package_db.find_one(key)

        logging.info("Resolving %s-%s", pkg, pkg_data["version"])

        # Use list because some package names may be invalid MongoDB keys
        # e.g., name = "abc.def"
        try:
            pkg_data["tree_created"] = [
                {"name": k, **v}
                for k, v in resolver.resolve(
                    pkg_data["requires_dist"], before=pkg_data["release_date"]
                ).items()
            ]
        except:
            logging.error("Cannot resolve created tree %s-%s", pkg, pkg_data["version"])
            pkg_data["tree_created"] = []

        try:
            pkg_data["tree_latest"] = [
                {"name": k, **v}
                for k, v in resolver.resolve(
                    pkg_data["requires_dist"], before=datetime.now(tz=timezone.utc)
                ).items()
            ]
        except:
            logging.error("Cannot resolve latest tree %s-%s", pkg, pkg_data["version"])
            pkg_data["tree_latest"] = []

        package_db.replace_one(key, pkg_data)

    client.close()


def main():
    logging.basicConfig(
        format="%(asctime)s (Process %(process)d) [%(levelname)s] %(filename)s:%(lineno)d %(message)s",
        level=logging.INFO,
    )

    client = MongoClient("mongodb://localhost:27017/", tz_aware=True)

    logging.info("Locating packages without dependency trees...")

    query =  {"tree_created": {"$exists": False}}
    package_names = client["license"]["package"].distinct("name", query)
    logging.info("Found %d packages to build dependency trees", len(package_names))

    with mp.Pool(mp.cpu_count()) as pool:
        pool.map(build_dep_trees, package_names)
        
    client.close()


if __name__ == "__main__":
    main()
