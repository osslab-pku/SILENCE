import os
import re
import json
import logging
import difflib
import argparse
import subprocess

from typing import List, Set, Dict, Any
from pymongo import MongoClient
from dateutil.parser import parse as parse_date
from packaging.version import parse as parse_v
from resolver import DependencyResolver


def get_eval_samples(mongo_url: str) -> List[Dict[str, Any]]:
    # Source: https://hugovk.github.io/top-pypi-packages/
    with open("top-pypi-packages-30-days.min.json", "r") as f:
        top_pkgs = json.load(f)
    logging.info("Sampling top downloaded packages at %s", top_pkgs["last_update"])

    client = MongoClient(mongo_url, tz_aware=True)
    pypi_db = client["license"]["pypi"]
    results = []
    for row in top_pkgs["rows"]:
        # We retrieve metadata from our own replica, to avoid require_dist inconsistencies
        pkg = row["project"]
        all_meta = list(pypi_db.find({"name": pkg}))
        if len(all_meta) == 0:
            logging.warn("%s has no metadata", pkg)
            continue
        latest = sorted(all_meta, key=lambda x: parse_date(x["upload_time"]))[-1]
        deps = latest["requires_dist"]

        # Skips packages with no dependencies
        if len(deps) == 0:
            continue

        logging.info("%s-%s: %d deps\n\t%s", pkg, latest["version"], len(deps), deps)
        results.append({"name": pkg, "version": latest["version"], "requires": deps})
    client.close()

    logging.info("%d of %d packages with deps", len(results), len(top_pkgs["rows"]))
    return results


def resolve_dependency_tree_pip(pkg: str, ver: str) -> str:
    def list_conda_envs() -> Set[str]:
        result = json.loads(
            subprocess.run(
                ["conda", "info", "--envs", "--json"],
                stdout=subprocess.PIPE,
            ).stdout.decode("utf-8", "ignore")
        )
        envs = set()
        for env in result["envs"]:
            for dir in result["envs_dirs"]:
                if env.startswith(dir):
                    envs.add(os.path.relpath(env, dir))
        return env

    def create_env(env_name: str, pkg: str, ver: str) -> bool:
        if env_name in list_conda_envs():
            logging.info(f"Environment {env_name} already exists")
            return False
        subprocess.run(["conda", "create", "-y", "--name", env_name, "python=3.9"])
        result = subprocess.run(
            [
                "conda",
                "run",
                "-n",
                env_name,
                "python",
                "-m",
                "pip",
                "install",
                f"{pkg}=={ver}",
                "pipdeptree",
            ]
        )
        if result.returncode != 0:
            return False
        return True

    def remove_env(env_name: str):
        subprocess.run(["conda", "remove", "-y", "--name", env_name, "--all"])

    env_name = f"dep_resolve_{pkg}_{ver}"

    if not create_env(env_name, pkg, ver):
        logging.error("Failed to create environment %s", env_name)
        return None

    logging.info("Created env %s for %s-%s", env_name, pkg, ver)

    dep_tree = subprocess.run(
        ["conda", "run", "-n", env_name, "pipdeptree", "-p", pkg],
        stdout=subprocess.PIPE,
    ).stdout.decode("utf-8", "ignore")

    remove_env(env_name)

    logging.info("Resolved tree: \n%s", dep_tree)
    return dep_tree


def compare_dep_trees(pkg: str, ver: str, dep_tree_pip: str, dep_tree: dict) -> dict:
    stat = {}

    deps_pip = set()
    for line in dep_tree_pip.strip().splitlines():
        if not line.startswith(" "):
            continue
        regex = re.compile(r"\- (.+) \[required: (.*), installed: (.*)\]")
        dep, spec, dep_ver = regex.findall(line)[0]

        # It is possible that pip resolved dep trees contain latest versions not
        # included in our metadata copy. If so, uses the latest version in our tree.
        if dep in dep_tree and parse_v(dep_ver) > parse_v(dep_tree[dep]["version"]):
            dep_ver = dep_tree[dep]["version"]

        deps_pip.add((dep, dep_ver))
    deps_pip_seq = [f"{dep}=={ver}" for dep, ver in sorted(deps_pip)]

    deps_ours = set()
    for dep, constraint in dep_tree.items():
        deps_ours.add((dep, constraint["version"]))
    deps_ours_seq = [f"{dep}=={ver}" for dep, ver in sorted(deps_ours)]

    stat["hit"] = len(deps_pip.intersection(deps_ours))
    stat["miss"] = len(deps_pip.difference(deps_ours))
    stat["excess"] = len(deps_ours.difference(deps_pip))
    stat["exact"] = int(stat["miss"] == 0 and stat["excess"] == 0)
    stat["precision"] = stat["hit"] / (stat["hit"] + stat["excess"])
    stat["recall"] = stat["hit"] / (stat["hit"] + stat["miss"])

    logging.info(
        "%s-%s: %d pip, %d ours, %d hit, %d miss, %d excess",
        pkg,
        ver,
        len(deps_pip),
        len(deps_ours),
        len(deps_pip.intersection(deps_ours)),
        len(deps_pip.difference(deps_ours)),
        len(deps_ours.difference(deps_pip)),
    )
    logging.info(
        "Dependency tree differences:\n%s",
        "\n".join(difflib.unified_diff(deps_pip_seq, deps_ours_seq)),
    )

    return stat


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-pip", action="store_true", default=False)
    parser.add_argument("--mongo-url", default="mongodb://localhost:27017/")
    args = parser.parse_args()

    # Get evaluation samples
    if os.path.exists("eval_samples.json"):
        with open("eval_samples.json", "r") as f:
            eval_samples = json.load(f)
    else:
        eval_samples = get_eval_samples(args.mongo_url)
        with open("eval_samples.json", "w") as f:
            json.dump(eval_samples, f, indent=2)

    # Sample only packages with at least 1 non-optional dependencies
    many_dep = lambda x: len([r for r in x["requires"] if ";" not in r]) >= 1
    eval_samples = [x for x in eval_samples if many_dep(x)]
    logging.info("%d packages with >=1 non-optional deps", len(eval_samples))

    # Compare results from pip and our algorithm
    stats = []
    for sample in eval_samples:
        pkg, ver = sample["name"], sample["version"]
        logging.info("Evaluating %s-%s", pkg, ver)

        if os.path.exists(f"output_pip/{pkg}_{ver}.txt"):
            with open(f"output_pip/{pkg}_{ver}.txt", "r") as f:
                dep_tree_pip = f.read()
        elif args.skip_pip:
            continue
        else:
            dep_tree_pip = resolve_dependency_tree_pip(pkg, ver)
            if dep_tree_pip is not None:
                with open(f"output_pip/{pkg}_{ver}.txt", "w") as f:
                    f.write(dep_tree_pip)
            else:
                continue

        if os.path.exists(f"output/{pkg}_{ver}.json"):
            with open(f"output/{pkg}_{ver}.json", "r") as f:
                dep_tree = json.load(f)
        else:
            dep_tree = DependencyResolver(args.mongo_url).resolve(sample["requires"])
            with open(f"output/{pkg}_{ver}.json", "w") as f:
                json.dump(dep_tree, f, indent=2)

        if dep_tree_pip.strip() == "" or len(dep_tree) == 0:
            continue

        stats.append(compare_dep_trees(pkg, ver, dep_tree_pip, dep_tree))

    logging.info(
        "%d total hit, %d total miss, %d total excess, %d / %d exact match packages",
        sum(stat["hit"] for stat in stats),
        sum(stat["miss"] for stat in stats),
        sum(stat["excess"] for stat in stats),
        sum(stat["exact"] for stat in stats),
        len(stats),
    )
    logging.info(
        "Coverage: %.4f, weighted precision: %.4f, weighted recall: %.4f",
        sum(s["hit"] for s in stats) / sum(s["hit"] + s["miss"] for s in stats),
        sum(stat["precision"] for stat in stats) / len(stats),
        sum(stat["recall"] for stat in stats) / len(stats),
    )


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s (Process %(process)d) [%(levelname)s] %(filename)s:%(lineno)d %(message)s",
        level=logging.DEBUG,
    )

    main()
