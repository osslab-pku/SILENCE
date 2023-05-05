# Understanding and Remediating Open-Source License Incompatibilities in the PyPI Ecosystem

## Intorduction
In this paper, we propose SILENCE, an SMT
(i.e., satisfiability modulo theories) based approach to automatically recommend actions to remediate license incompatibility in a release’s dependency graph. Given a dependency graph
with one or more license incompatibilities, SILENCE searches for an alternative graph without license incompatibilities while minimizing its differences from the original graph.



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
