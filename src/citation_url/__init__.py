"""Parse URLs for DOIs, PubMed identifiers, PMC identifiers, arXiv identifiers, etc."""

import enum
from collections import defaultdict
from collections.abc import Iterable, Mapping
from typing import Literal, overload
from urllib.parse import urlparse

from curies import Reference

__all__ = [
    "FailureReason",
    "group",
    "parse",
]

PROTOCOLS = {"https://", "http://"}

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
    "www.frontiersin.org/articles/": "doi",
    "arxiv.org/pdf/": "arxiv",
    "arxiv.org/abs/": "arxiv",
    "ar5iv.org/abs/": "arxiv",
    "ar5iv.org/pdf/": "arxiv",
    "ar5iv.org/html/": "arxiv",
    "www.sciencedirect.com/science/article/pii/": "pii",
}

#: from https://dtds.rsc.org/#desc-journalref
RSC_JOURNAL_TWO_LETTER_CODES = {
    "AC",
    "AN",
    "CC",
    "CE",
    "CP",
    "CS",
    "DT",
    "EM",
    "FD",
    "FT",
    "GC",
    "GT",
    "IC",
    "OC",
    "PC",
    "JA",
    "JC",
    "JM",
    "MC",
    "NJ",
    "NP",
    "P1",
    "P2",
    "PO",
    "RC",
    "RE",
    "PY",
    "SU",
}

DOI_REWRITES = {}

# Add RSC journal abbreviations from https://dtds.rsc.org/#desc-journalref
for _year in range(1960, 2100):
    for _journal in RSC_JOURNAL_TWO_LETTER_CODES:
        for _protocol in PROTOCOLS:
            _key = f"{_protocol}pubs.rsc.org/en/Content/ArticleLanding/{_year}/{_journal}/"
            DOI_REWRITES[_key] = "10.1039/"

IRRECONCILABLE = [
    "www.pnas.org/content/pnas/early/",
    "www.pnas.org/content/pnas/",
    "www.cell.com/article/",
    "pdfs.semanticscholar.org",
    "www.cell.com/cell-systems/fulltext/",
    "www.cell.com/cell/pdf/",
    "msb.embopress.org/content/",
    "msb.embopress.org/content/msb/",
]


class FailureReason(enum.Enum):
    """A result type enumeration."""

    unknown = "unknown"
    irreconcilable = "irreconcilable"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}.{self.value}"


def parse(url: str) -> Reference | FailureReason:
    """Normalize a citation string that might be a crazy URL from a publisher.

    :param url: A URL or other string that can be interpreted as a citation
    :returns: Either a pair of two strings (e.g., a prefix and identifier) if
        the URL could be successfully parsed, or a pair of None and the input
        if it could not be parsed.

    Ideally, this function should be able to parse a huge amount of garbage.

    >>> parse("https://joss.theoj.org/papers/10.21105/joss.01708")
    Reference(prefix='doi', identifier='10.21105/joss.01708')

    >>> parse("http://www.ncbi.nlm.nih.gov/pubmed/34739845")
    Reference(prefix='pubmed', identifier='34739845')

    >>> parse("http://www.ncbi.nlm.nih.gov/pubmed/29199020,%2029199020")
    Reference(prefix='pubmed', identifier='29199020')

    >>> parse("http://www.biorxiv.org/content/early/2017/08/09/174094")
    Reference(prefix='doi', identifier='10.1101/174094')

    >>> parse("http://www.biorxiv.org/content/biorxiv/early/2017/08/09/174094.full.pdf")
    Reference(prefix='doi', identifier='10.1101/174094')
    """
    if url.isnumeric():
        return Reference(prefix="pubmed", identifier=url)

    for url_prefix, doi_prefix in DOI_REWRITES.items():
        if url.startswith(url_prefix):
            doi = doi_prefix + url.removeprefix(url_prefix)
            return Reference(prefix="doi", identifier=doi)

    for protocol in PROTOCOLS:
        if url.startswith(protocol):
            return _handle(url.removeprefix(protocol))

    for doi_prefix in RAW_DOI_PREFIXES:
        if url.startswith(doi_prefix):
            doi = url.removesuffix(".pdf")
            for version in range(10):
                doi = doi.removesuffix(f".v{version}")
            return Reference(prefix="doi", identifier=doi)

    return FailureReason.unknown


def _handle(url: str) -> Reference | FailureReason:  # noqa:C901
    if any(url.startswith(x) for x in IRRECONCILABLE):
        return FailureReason.irreconcilable

    for suffix in SUFFIXES:
        url = url.removesuffix(suffix)

    if url.startswith("www.jbc.org/content/") and all(x.isnumeric() for x in url.split("/")[2:]):
        return FailureReason.irreconcilable

    if url.startswith("www.ncbi.nlm.nih.gov/pubmed/"):
        pubmed_id = url[len("www.ncbi.nlm.nih.gov/pubmed/") :]
        if "," in pubmed_id:
            pubmed_id = pubmed_id.split(",")[0]
        return Reference(prefix="pubmed", identifier=pubmed_id)

    for prefix, ns in PREFIXES.items():
        if url.startswith(prefix):
            return Reference(prefix=ns, identifier=url.removeprefix(prefix))

    if url.startswith("www.ncbi.nlm.nih.gov/pmc/articles/"):
        url = url[len("www.ncbi.nlm.nih.gov/pmc/articles/") :]
        url = url.split("/")[0]
        return Reference(prefix="pmc", identifier=url)

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
            return Reference(prefix="doi", identifier=f"10.1101/{biorxiv_id}")

    if url.startswith("europepmc.org/article/PMC/"):
        pmc_id = url.removeprefix("europepmc.org/article/PMC/")
        return Reference(prefix="pmc", identifier=f"PMC{pmc_id}")

    if url.lower().startswith("europepmc.org/articles/pmc"):
        url = url.lower().removeprefix("europepmc.org/articles/pmc")
        pmc_id = url.split("?")[0]
        return Reference(prefix="pmc", identifier=f"PMC{pmc_id}")

    if url.startswith("www.jbc.org/content/early/"):
        url = url.removeprefix("www.jbc.org/content/early/")
        parts = url.split("/")  # first 3 are dates, forth should be what we want
        return Reference(prefix="doi", identifier=f"10.1074/{parts[3]}")

    if url.startswith("www.biorxiv.org/content/"):
        url = url.removeprefix("www.biorxiv.org/content/")
        for v in range(10):
            url = url.removesuffix(f"v{v}")
        return Reference(prefix="doi", identifier=url)

    if url.startswith("www.preprints.org/manuscript/"):
        url = url.removeprefix("www.preprints.org/manuscript/")
        for v in range(10):
            url = url.removesuffix(f"/v{v}")
        return Reference(prefix="doi", identifier=f"10.20944/preprints{url}")

    if url.startswith("www.frontiersin.org/article/"):
        doi = url.removeprefix("www.frontiersin.org/article/").removesuffix("/full")
        return Reference(prefix="doi", identifier=doi)

    if url.startswith("www.nature.com/articles/"):
        url = url.removeprefix("www.nature.com/articles/")
        url = url.removesuffix(".pdf")
        return Reference(prefix="doi", identifier=f"10.1038/{url}")

    if url.startswith("journals.plos.org/ploscompbiol/article/file"):
        query = _get_query(url)
        return Reference(prefix="doi", identifier=query["id"])

    if url.startswith("elifesciences.org/download/"):
        url = url.removeprefix("elifesciences.org/download/")
        part = url.split("/")[1]
        part = part.split("?")[0]
        elife_id = part.split("-")[1]
        return Reference(prefix="doi", identifier=f"10.7554/eLife.{elife_id}")

    if url.startswith("pubs.acs.org/accacs/article/doi/"):
        rest = url.removeprefix("pubs.acs.org/accacs/article/doi/")
        a, b, _rest = rest.split("/", maxsplit=2)
        return Reference(prefix="doi", identifier=a + "/" + b)

    if url.startswith("eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi"):
        query = _get_query(url)
        if query.get("dbfrom") == "pubmed":
            return Reference(prefix="pubmed", identifier=query["id"])

    return FailureReason.unknown


def _get_query(url: str) -> Mapping[str, str]:
    query = {}
    for part in urlparse(url.replace("&amp;", "&")).query.split("&"):
        key, value = part.split("=")
        query[key] = value
    return query


# docstr-coverage:excused `overload`
@overload
def group(urls: Iterable[str], *, keep_none: Literal[False] = ...) -> dict[str, set[str]]: ...


# docstr-coverage:excused `overload`
@overload
def group(
    urls: Iterable[str], *, keep_none: Literal[True] = ...
) -> dict[str | FailureReason, set[str]]: ...


def group(
    urls: Iterable[str], *, keep_none: bool = True
) -> dict[str | FailureReason, set[str]] | dict[str, set[str]]:
    """Return a dictionary of the parsed URLs."""
    rv: defaultdict[str | FailureReason, set[str]] = defaultdict(set)
    for url in urls:
        match parse(url):
            case Reference() as reference:
                rv[str(reference.prefix)].add(reference.identifier)
            case FailureReason() as reason:
                if keep_none:
                    rv[reason].add(url)
    return dict(rv)
