# dep_resolve: Python Dependency Tree Resolution

This module imitates the behavior of pip based on a MongoDB replica of PyPI using the algorithm described in Wang et al. [1], which is a simple breadth first search algorithm that ignores dependency conflicts and does not conduct any backtracking.

## Files

1. `resolver.py`: The dependency resolver
2. `evaluate.py`: The script that compares the resolved dependency trees with trees resolved from PyPI
3. `eval_samples.json`: The packages used for evaluation
4. `output/`: Dependency tree resolved from our resolver
5. `output_pip/`: Dependency trees resolved from pip

## Evaluation Results

```
4755 total hit, 666 total miss, 193 total excess, 60 / 179 exact match packages
coverage: 0.8771, weighted precision: 0.9695, weighted recall: 0.9144
```

## References

1. Wang, Ying, et al. "Watchman: Monitoring Dependency Conflicts for Python Library Ecosystem." Proceedings of the ACM/IEEE 42nd International Conference on Software Engineering. 2020.