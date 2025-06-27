[![CI](https://github.com/Villtord/B07-nxs2txt/actions/workflows/ci.yml/badge.svg)](https://github.com/Villtord/B07-nxs2txt/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/gh/Villtord/B07-nxs2txt/branch/main/graph/badge.svg)](https://codecov.io/gh/Villtord/B07-nxs2txt)
[![PyPI](https://img.shields.io/pypi/v/B07-nxs2txt.svg)](https://pypi.org/project/B07-nxs2txt)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://www.apache.org/licenses/LICENSE-2.0)

# B07nxs2txt

convertion script from nexus to txt for DLS B07 beamlines

If you use it from DLS without installing package:

```
module load python
...

python /dls_sw/b07/scripts/Data_Handling/cuddle/src/B07nxs2txt path_to_files
```

If you use development container environment assuming venv is configured and activated:

```
 python -m B07nxs2txt path_to_files
```

This is where you should write a short paragraph that describes what your module does,
how it does it, and why people should use it.

Source          | <https://github.com/Villtord/B07-nxs2txt>
:---:           | :---:
Releases        | <https://github.com/Villtord/B07-nxs2txt/releases>

This is where you should put some images or code snippets that illustrate
some relevant examples. If it is a library then you might put some
introductory code here:

```python
$ python -m B07nxs2txt --help
usage: __main__.py [-h] [-v] [--titles_off] folderpath

positional arguments:
  folderpath     Full path to nxs folder to convert files

options:
  -h, --help     show this help message and exit
  -v, --version  show program's version number and exit
  --titles_off   Switch OFF column titles
```
