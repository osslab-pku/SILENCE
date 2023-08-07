# SILENSE

This repository contains source code and data of the papar "Understanding and Remediating Open-Source License Incompatibilities in the PyPI Ecosystem".

## Intorduction
In this paper, we first conduct a large-scale empirical study of license incompatibility in PyPI ecosystem. Inspired by our findings, we propose SILENSE, an SMT-solver-based incompatibility remediator for licenses in the
dependency graph. Given a release and its dependency graph with one or more license incompatibilities, SILENSE 1) finds alternative licenses that are compatible with the dependency
graph, and 2) searches for alternative graphs with no license incompatibilities and minimal difference with the original graph. The results are aggregated as a report of recommended
remediations (i.e., migrations, removals, version pinnings, or license changes) for developers to consider.


## Dirs and files
1. `licensing_data_collection`: licensing information collection
2. `dep_resolve` : Python dependency tree resolution
3. `knowledge_base` contains license compatibility matrix, migration patterns, license keywords and so on.
4. `analysis.py` : data analysis of empirical study
5. `RQ1_license_distribution.ipynb`: results of RQ1
6. `RQ1_license_evolution.ipynb`: results of RQ1
7. `RQ2_license_incompatibility.ipynb`: results of RQ2
8. `RQ3_license_remediation_practice.md`: note of RQ3
9. `remediator.py`: implementation of SILENSE's SMT-based part
10. `relicenser.py`: implementation of SILENSE's relicenser
11. `res` contains results and evaluation of SILENSE.
12. `data` contains our dataset
13. `SILENSE.py` contains the main function of SILENSE.


## How to start?

1. The dataset is stored in the `package` collection in the `license` database. You can get the dataset in `data` directory (due to the file size limit on GitHub, please download the dataset at [here](https://figshare.com/s/1fcea61928e416533380)) and you need to import it into MongoDB. Run:
```
mongorestore --db=license --gzip data/package.bson.gz
```

2. For results of the empirical study, you can run:
```
RQ1_license_distribution.ipynb
RQ1_license_evolution.ipynb
RQ2_license_incompatibility.ipynb
```

3. To get remediations of all incompatibilities in top 5,000 downloaded packages, you can run:
```
python remediator.py all
python relicenser.py
```

4. If you want to get remediations in dependency graph for a specific package version, run:
```
python SILENSE.py -n name -v version
```

For example, if you want to get remediations for fiftyone 0.18.0 in the paper, you can run:
```
python SILENSE.py -n fiftyone -v 0.18.0
```

you will get the output as follows:
```
Possible Remediations for fiftyone 0.18.0:
1. Change project license to GPL-3.0-only, GPL-3.0-or-later, or AGPL-3.0-only;
2. Or make the following dependency changes:
   a) Remove ndjson;
   b) Pin voxel51-eta to 0.1.9;
   c) Pin pillow to 6.2.2;
   d) Pin imageio to 2.9.0;
   e) Pin h11 to 0.11.0.
3. Or make the following dependency changes:
   a) Remove voxel51-eta;
   b) Remove ndjson;
   c) Pin h11 to 0.11.0.
```

## License
The project is licensed under [MulanPubL-2.0](LISENSE).


## Citation
For citing, please use following BibTex citation:
```
@inproceedings{SILENSE2023,
  author       = {Weiwei Xu and
                  Hao He and
                  Kai Gao and
                  Minghui Zhou},
  title        = {Understanding and Remediating Open-Source License Incompatibilities in the PyPI Ecosystem},
  booktitle    = {38th {IEEE/ACM} International Conference on Automated Software Engineering,
                  {ASE} 2023, Luxembourg, September 11-15, 2023.}
}
```
