<!--
<p align="center">
  <img src="https://github.com/cthoyt/citation-url/raw/main/docs/source/logo.png" height="150">
</p>
-->

<h1 align="center">
  citation-url
</h1>

<p align="center">
    <a href="https://github.com/cthoyt/citation-url/actions?query=workflow%3ATests">
        <img alt="Tests" src="https://github.com/cthoyt/citation-url/workflows/Tests/badge.svg" />
    </a>
    <a href="https://github.com/cthoyt/cookiecutter-python-package">
        <img alt="Cookiecutter template from @cthoyt" src="https://img.shields.io/badge/Cookiecutter-python--package-yellow" /> 
    </a>
    <a href="https://pypi.org/project/citation_url">
        <img alt="PyPI" src="https://img.shields.io/pypi/v/citation-url" />
    </a>
    <a href="https://pypi.org/project/citation_url">
        <img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/citation-url" />
    </a>
    <a href="https://github.com/cthoyt/citation-url/blob/main/LICENSE">
        <img alt="PyPI - License" src="https://img.shields.io/pypi/l/citation-url" />
    </a>
    <!--
    <a href='https://citation_url.readthedocs.io/en/latest/?badge=latest'>
        <img src='https://readthedocs.org/projects/citation_url/badge/?version=latest' alt='Documentation Status' />
    </a>
    -->
    <a href='https://github.com/psf/black'>
        <img src='https://img.shields.io/badge/code%20style-black-000000.svg' alt='Code style: black' />
    </a>
</p>

Parse URLs for DOIs, PubMed identifiers, PMC identifiers, arXiv identifiers, etc.

This module has a single `parse()` function that takes in a URL and gives back
a CURIE pair (with `None` as the first entry if it could not parse)

```python
>>> import citation_url
>>> citation_url.parse("https://joss.theoj.org/papers/10.21105/joss.01708")
('doi', '10.21105/joss.01708')
>>> citation_url.parse("http://www.ncbi.nlm.nih.gov/pubmed/34739845")
('pubmed', '34739845')
>>> citation_url.parse("https://example.com/true-garbage")
(None, 'https://example.com/true-garbage')
```

## 🚀 Installation

The most recent release can be installed from
[PyPI](https://pypi.org/project/citation_url/) with:

```bash
$ pip install citation_url
```

The most recent code and data can be installed directly from GitHub with:

```bash
$ pip install git+https://github.com/cthoyt/citation-url.git
```

## 👐 Contributing

Contributions, whether filing an issue, making a pull request, or forking, are appreciated. See
[CONTRIBUTING.md](https://github.com/cthoyt/citation-url/blob/master/.github/CONTRIBUTING.md) for more information on getting involved.

## 👋 Attribution

### ⚖️ License

The code in this package is licensed under the MIT License.

<!--
### 📖 Citation

Citation goes here!
-->

<!--
### 🎁 Support

This project has been supported by the following organizations (in alphabetical order):

- [Harvard Program in Therapeutic Science - Laboratory of Systems Pharmacology](https://hits.harvard.edu/the-program/laboratory-of-systems-pharmacology/)

-->

<!--
### 💰 Funding

This project has been supported by the following grants:

| Funding Body                                             | Program                                                                                                                       | Grant           |
|----------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------|-----------------|
| DARPA                                                    | [Automating Scientific Knowledge Extraction (ASKE)](https://www.darpa.mil/program/automating-scientific-knowledge-extraction) | HR00111990009   |
-->

### 🍪 Cookiecutter

This package was created with [@audreyfeldroy](https://github.com/audreyfeldroy)'s
[cookiecutter](https://github.com/cookiecutter/cookiecutter) package using [@cthoyt](https://github.com/cthoyt)'s
[cookiecutter-snekpack](https://github.com/cthoyt/cookiecutter-snekpack) template.

## 🛠️ For Developers

<details>
  <summary>See developer instrutions</summary>

The final section of the README is for if you want to get involved by making a code contribution.

### Development Installation

To install in development mode, use the following:

```bash
$ git clone git+https://github.com/cthoyt/citation-url.git
$ cd citation-url
$ pip install -e .
```

### 🥼 Testing

After cloning the repository and installing `tox` with `pip install tox`, the unit tests in the `tests/` folder can be
run reproducibly with:

```shell
$ tox
```

Additionally, these tests are automatically re-run with each commit in a [GitHub Action](https://github.com/cthoyt/citation-url/actions?query=workflow%3ATests).

### 📖 Building the Documentation

```shell
$ tox -e docs
``` 

### 📦 Making a Release

After installing the package in development mode and installing
`tox` with `pip install tox`, the commands for making a new release are contained within the `finish` environment
in `tox.ini`. Run the following from the shell:

```shell
$ tox -e finish
```

This script does the following:

1. Uses [Bump2Version](https://github.com/c4urself/bump2version) to switch the version number in the `setup.cfg` and
   `src/citation_url/version.py` to not have the `-dev` suffix
2. Packages the code in both a tar archive and a wheel
3. Uploads to PyPI using `twine`. Be sure to have a `.pypirc` file configured to avoid the need for manual input at this
   step
4. Push to GitHub. You'll need to make a release going with the commit where the version was bumped.
5. Bump the version to the next patch. If you made big changes and want to bump the version by minor, you can
   use `tox -e bumpversion minor` after.
</details>
