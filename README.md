# varscan-tool

VarScan is a platform-independent mutation caller for targeted, exome, and whole-genome resequencing data generated on Illumina, SOLiD, Life/PGM, Roche/454, and similar instruments.

## Installation

```sh
pip install .
```

## Development

* Clone this repository
* Requirements:
  * Python >= 3.9
  * Tox
* `make venv` to create a virtualenv
* `source .venv/bin/activate` to activate new virtualenv
* `make init` to install dependencies and pre-commit hooks
