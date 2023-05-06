# licensing data collection

This module collects licensing information for 3,622,711 package versions in the PyPI ecosystem.

## Files:
1. `build_pypi_packages.py` builds the initial dataset from PyPI metadata.
2. `clean2dirty_count.py` builds a mapping between license fields and SPDX license identifiers
using all package versions with available classifier tags.
3. `clean_license.py` : clean `license` filed
4. `download_dis.py`  : download distributions of packages whose license information is missing
5. `get_license_file.py` : get `LISENCE` and `README` files in the distribution
6. `scan_code.py` : use scancode to obtain license information in the `LISENCE` and `README` files
7. `license_evaluation.csv` : the evaluation of the license information we identified
## Evaluation results

To evaluate the effectiveness of our license identification approach, we randomly select 385 package versions from the total 3,622,711 package versions (confidence level = 95%, margin of error = 5%). We check whether the licenses identified by our approach can match different sources of information, including: 1) GitHub repositories), 2) LICENSE files in the distribution, and 3) the license field.

Among the385 samples, our approach returns Unrecognizable for 51 of them (13.2%). Of the remaining 334 samples, 323 of them match other sources of information, resulting in an accuracy of 96.7% (323 / 334)