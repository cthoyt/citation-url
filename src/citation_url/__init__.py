# -*- coding: utf-8 -*-

"""Parse URLs for DOIs, PubMed identifiers, PMC identifiers, arXiv identifiers, etc."""

from collections import defaultdict
from typing import DefaultDict, Dict, Iterable, List, Optional, Set, Tuple, Union

__all__ = [
    "parse",
    "sort_key",
    "parse_many",
    "group",
]

RAW_DOI_PREFIXES = {"10.21203/", "10.26434/", "10.20944/", "10.21105/"}

SUFFIXES = [".pdf", ".full", ".full.pdf", ".article-metrics", "/pdf"]

PREFIXES = {
    "doi.org/": "doi",
    "biorxiv.org/lookup/doi/": "biorxiv",
    "medrxiv.org/lookup/doi/": "medrxiv",
    "jvi.asm.org/cgi/doi/": "doi",
    "www.sciencemag.org/lookup/doi/": "doi",
    "doi.wiley.com/": "doi",
    "onlinelibrary.wiley.com/doi/full/": "doi",
    "bmcsystbiol.biomedcentral.com/articles/": "doi",
    "dx.plos.org/": "doi",
    "www.nejm.org/doi/": "doi",
    "onlinelibrary.wiley.com/doi/abs/": "doi",
    "www.pnas.org/cgi/doi/": "doi",
    "www.microbiologyresearch.org/content/journal/jgv/": "doi",
    "link.springer.com/": "doi",
    "jcm.asm.org/lookup/doi/": "doi",
    "www.tandfonline.com/doi/": "doi",
    "www.annualreviews.org/doi/": "doi",
    "joss.theoj.org/papers/": "doi",
    "bmcbioinformatics.biomedcentral.com/track/pdf/": "doi",
}

PROTOCOLS = {"https://", "http://"}

Identifier = Tuple[str, str]
Failure = Tuple[None, str]
Result = Union[Identifier, Failure]


def parse(url: str) -> Result:
    """Normalize a citation string that might be a crazy URL from a publisher.

    :param url: A URL or other string that can be interpreted as a citation
    :returns: Either a pair of two strings (e.g., a prefix and identifier) if
        the URL could be successfully parsed, or a pair of None and the input
        if it could not be parsed.

    Ideally, this function should be able to parse a huge amount of garbage.

    >>> parse("https://joss.theoj.org/papers/10.21105/joss.01708")
    ('doi', '10.21105/joss.01708')

    >>> parse("http://www.ncbi.nlm.nih.gov/pubmed/34739845")
    ('pubmed', '34739845')

    >>> parse("http://www.ncbi.nlm.nih.gov/pubmed/29199020,%2029199020")
    ('pubmed', '29199020')

    >>> parse("http://www.biorxiv.org/content/early/2017/08/09/174094")
    ('doi', '10.1101/174094')

    >>> parse("http://www.biorxiv.org/content/biorxiv/early/2017/08/09/174094.full.pdf")
    ('doi', '10.1101/174094')
    """
    if url.isalnum():
        return "pubmed", url

    for protocol in PROTOCOLS:
        if url.startswith(protocol):
            return _handle(url[len(protocol) :])

    for doi_prefix in RAW_DOI_PREFIXES:
        if url.endswith(".pdf"):
            url = url[: -len(".pdf")]
        if url.startswith(doi_prefix):
            for version in range(10):
                if url.endswith(f".v{version}"):
                    url = url[: -len(f".v{version}")]
            return "doi", url

    return None, url


def _handle(url: str) -> Result:
    for suffix in SUFFIXES:
        if url.endswith(suffix):
            url = url[: -len(suffix)]

    if url.startswith("www.ncbi.nlm.nih.gov/pubmed/"):
        pubmed_id = url[len("www.ncbi.nlm.nih.gov/pubmed/") :]
        if "," in pubmed_id:
            pubmed_id = pubmed_id.split(",")[0]
        return "pubmed", pubmed_id

    for prefix, ns in PREFIXES.items():
        if url.startswith(prefix):
            return ns, url[len(prefix) :]

    if url.startswith("www.ncbi.nlm.nih.gov/pmc/articles/"):
        url = url[len("www.ncbi.nlm.nih.gov/pmc/articles/") :]
        url = url.split("/")[0]
        return "pmc", url

    for prefix in (
        "www.biorxiv.org/content/early/",
        "www.biorxiv.org/content/biorxiv/early/",
    ):
        if url.startswith(prefix):
            url = url[len(prefix) :]
            parts = url.split("/")  # first 3 are dates, forth should be what we want
            biorxiv_id = parts[3]
            if "v" in biorxiv_id:
                biorxiv_id = biorxiv_id.split("v")[0]
            return "doi", f"10.1101/{biorxiv_id}"

    if url.startswith("www.biorxiv.org/content/"):
        url = url[len("www.biorxiv.org/content/") :].rstrip()
        for v in range(10):
            if url.endswith(f"v{v}"):
                url = url[: -len(f"v{v}")]
        return "doi", url

    if url.startswith("www.preprints.org/manuscript/"):
        url = url[len("www.preprints.org/manuscript/") :]
        for v in range(10):
            if url.endswith(f"/v{v}"):
                url = url[: -len(f"/v{v}")]
        return "doi", f"10.20944/preprints{url}"

    if url.startswith("www.frontiersin.org/article/"):
        url = url[len("www.frontiersin.org/article/") :]
        if url.endswith("/full"):
            url = url[: -len("/full")]
        return "doi", url

    if url.startswith("www.nature.com/articles/"):
        url = url[len("www.nature.com/articles/") :]
        if url.endswith(".pdf"):
            url = url[: -len(".pdf")]
        return "doi", f"10.1038/{url}"

    return None, url


def sort_key(item: Result) -> Tuple[int, str, str]:
    """Sort results."""
    if item[0] is None:
        return 1, "", item[1]
    return 0, item[0], item[1]


def group(urls: Iterable[str], *, keep_none: bool = True) -> Dict[Optional[str], Set[str]]:
    """Return a dictionary of the parsed URLs."""
    rv: DefaultDict[Optional[str], Set[str]] = defaultdict(set)
    for url in urls:
        prefix, identifier = parse(url)
        if prefix is None and not keep_none:
            continue
        rv[prefix].add(identifier)
    return dict(rv)


def parse_many(urls: Iterable[str], pre_sort: bool = False) -> List[Result]:
    """Parse an iterable of URLs."""
    if pre_sort:
        urls = sorted(urls)
    return [parse(url) for url in urls]
