# -*- coding: utf-8 -*-

"""Parse URLs for DOIs, PubMed identifiers, PMC identifiers, arXiv identifiers, etc."""

from typing import Tuple, Union

__all__ = [
    "parse",
]

RAW_DOI_PREFIXES = {
    "10.21203/",
    "10.26434/",
    "10.20944/",
}

PREFIXES = {
    "https://doi.org/": "doi",
    "http://biorxiv.org/lookup/doi/": "biorxiv",
    "http://medrxiv.org/lookup/doi/": "medrxiv",
    "http://jvi.asm.org/cgi/doi/": "doi",
    "https://www.sciencemag.org/lookup/doi/": "doi",
    "http://doi.wiley.com/": "doi",
    "https://onlinelibrary.wiley.com/doi/full/": "doi",
    "http://bmcsystbiol.biomedcentral.com/articles/": "doi",
    "https://dx.plos.org/": "doi",
    "http://www.nejm.org/doi/": "doi",
    "https://onlinelibrary.wiley.com/doi/abs/": "doi",
    "http://www.pnas.org/cgi/doi/": "doi",
    "https://www.microbiologyresearch.org/content/journal/jgv/": "doi",
    "http://link.springer.com/": "doi",
    "http://jcm.asm.org/lookup/doi/": "doi",
    "https://www.tandfonline.com/doi/": "doi",
    "https://www.annualreviews.org/doi/": "doi",
    "http://www.ncbi.nlm.nih.gov/pubmed/": "pubmed",
    "https://www.ncbi.nlm.nih.gov/pubmed/": "pubmed",
    "https://joss.theoj.org/papers/": "doi",
}


def parse(url: str) -> Union[Tuple[str, str], Tuple[None, str]]:
    """Normalize a citation string that might be a crazy URL from a publisher.

    :param url: A URL
    :returns: Either a pair of two strings (e.g., a prefix and identifier) if
        the URL could be successfully parsed, or a pair of None and the input
        if it could not be parsed.

    Ideally, this function should be able to parse a huge amount of garbage.

    >>> parse("https://joss.theoj.org/papers/10.21105/joss.01708")
    ('doi', '10.21105/joss.01708')
    >>> parse("http://www.ncbi.nlm.nih.gov/pubmed/34739845")
    ('pubmed', '34739845')
    """
    if url.isalnum():
        return "pubmed", url

    for prefix in RAW_DOI_PREFIXES:
        if url.startswith(prefix):
            for v in range(10):
                if url.endswith(f".v{v}"):
                    url = url[: -len(f".v{v}")]
            return "doi", url

    for prefix, ns in PREFIXES.items():
        if url.startswith(prefix):
            return ns, url[len(prefix) :]

    if url.startswith("https://www.ncbi.nlm.nih.gov/pmc/articles/"):
        url = url[len("https://www.ncbi.nlm.nih.gov/pmc/articles/") :]
        url = url.rstrip("/")
        return "pmc", url

    if url.startswith("http://www.biorxiv.org/content/early/"):
        url = url[len("http://www.biorxiv.org/content/early/") :]
        parts = url.split("/")  # first 3 are dates, forth should be what we want
        biorxiv_id = parts[3]
        if "v" in biorxiv_id:
            biorxiv_id = biorxiv_id.split("v")[0]
        return "doi", f"10.1101/{biorxiv_id}"

    if url.startswith("https://www.biorxiv.org/content/"):
        url = url[len("https://www.biorxiv.org/content/") :].rstrip()
        if url.endswith(".pdf"):
            url = url[: -len(".pdf")]
        if url.endswith(".full"):
            url = url[: -len(".full")]
        for v in range(10):
            if url.endswith(f"v{v}"):
                url = url[: -len(f"v{v}")]
        return "doi", url

    if url.startswith("https://www.preprints.org/manuscript/"):
        url = url[len("https://www.preprints.org/manuscript/") :]
        for v in range(10):
            if url.endswith(f"/v{v}"):
                url = url[: -len(f"/v{v}")]
        return "doi", f"10.20944/preprints{url}"

    if url.startswith("https://www.frontiersin.org/article/"):
        url = url[len("https://www.frontiersin.org/article/") :]
        if url.endswith("/full"):
            url = url[: -len("/full")]
        return "doi", url

    return None, url
