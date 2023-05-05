# Understanding and Remediating Open-Source License Incompatibilities in the PyPI Ecosystem

## Intorduction
In this paper, we propose SILENCE, an SMT-solver-based incompatibility remediator for licenses in the
dependency graph. Given a release and its dependency graph with one or more license incompatibilities, SILENCE 1) finds alternative licenses that are compatible with the dependency
graph, and 2) searches for alternative graphs with no license incompatibilities and minimal difference with the original graph. The results are aggregated as a report of recommended
remediations (i.e., migrations, removals, version pinnings, or license changes) for developers to consider.


## Dirs and files
1. `data_collection`: licensing information collection
2. `dep_resolve` : Python Dependency Tree Resolution
3. `knowledge_base` contains license compatibility matrix, migration patterns, license keywords and so on.
4. `res` contains results and evaluation of SILENCE.
5. `analysis.py` : data analysis of empirical study
6. `license_distribution.ipynb`: results of RQ1
7. `license_evolution.ipynb`: results of RQ1
8. `license_incompatibility.ipynb`: results of RQ2
9. `NOTE.md`: note of RQ3
9. `remediator.py`: implementation of SILENCE's SMT-based part
10. `relicenser.py`: implementation of SILENCE's relicenser
11. `data` contains our dataset


## How to start?

1. The dataset is stored in the `package` collection in the `license` database. You can get the dataset in `data` directory and you need to import it into MongoDB. Run:
```
mongorestore --db=license --gzip data/package.bson.gz
```

2. For results of the empirical study, you can run:
```
license_distribution.ipynb
license_evolution.ipynb
license_incompatibility.ipynb
```

3. To get remediations of all incompatibilities in top 5,000 downloaded packages, you can run:
```
python remediator.py all
python relicenser.py
```

4. If you want to get remediations in dependency graph for a specific package version, run:
```
python remediator.py one -n name -v version
```
