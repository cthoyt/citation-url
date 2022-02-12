"""Interface to EndNote."""

import time
from pathlib import Path
from typing import Dict, Iterable, Set, Union

import click
from defusedxml import ElementTree

from citation_url import Status, group


def process_endnote_xml(
    path: Union[str, Path], keep_none: bool = False
) -> Dict[Union[str, Status], Set[str]]:
    """Extract all URLs from an EndNote XML file."""
    tree = ElementTree.parse(path)
    groups = group(
        (
            element.text
            for query in ("text-urls", "pdf-urls")
            for element in tree.findall(f"records/record/urls/{query}/url")
            if element.text and element.text.startswith("http")
        ),
        keep_none=keep_none,
    )
    groups.setdefault("doi", set()).update(
        element.text
        for element in tree.findall("records/record/electronic-resource-num")
        if element.text
    )
    return groups


def endnote_to_wikidata(path: Union[str, Path]):
    """Ensure the contents of the EndNote XML file are added to Wikidata."""
    groups = process_endnote_xml(path=path, keep_none=False)
    _upload_wikidata(
        id_type="pmcid",
        source="europepmc",
        identifiers=[_removeprefix(x, "PMC") for x in groups.get("pmc", [])],
    )
    _upload_wikidata(id_type="doi", source="crossref", identifiers=groups.get("doi", []))
    _upload_wikidata(id_type="pmid", source="europepmc", identifiers=groups.get("pubmed", []))
    _upload_wikidata(id_type="arxiv", source="arxiv", identifiers=groups.get("arxiv", []))
    _upload_wikidata(id_type="biorxiv", source="biorxiv", identifiers=groups.get("biorxiv", []))


def _removeprefix(s: str, prefix: str) -> str:
    if s.startswith(prefix):
        return s[len(prefix) :]
    return s


def _upload_wikidata(id_type: str, source: str, identifiers: Iterable[str]):
    import pystow
    from tqdm import tqdm
    from wikidataintegrator import wdi_login
    from wikidataintegrator.wdi_helpers import PublicationHelper

    username = pystow.get_config("wikidata", "username")
    password = pystow.get_config("wikidata", "password")

    wikidata_login = wdi_login.WDLogin(username, password)

    for identifier in tqdm(identifiers, desc=f"{id_type}/{source}"):
        try:
            publication_helper = PublicationHelper(identifier, id_type=id_type, source=source)
            qid, warnings, success = publication_helper.get_or_create(wikidata_login)
            success = "success" if success is True else success
            tqdm.write(f"{id_type}:{identifier}\twikidata:{qid}\tmessage: {success}")
            for warning in warnings or []:
                tqdm.write(f"    warning: {warning}")
            time.sleep(3)
        except Exception as e:
            tqdm.write(f"{id_type}:{identifier}")
            tqdm.write(f"    failure: {e}")


@click.command()
@click.argument("path", type=click.Path(path_type=Path))
def main(path: Path):
    """Ensure the papers in a EndNote XML are added to Wikidata."""
    endnote_to_wikidata(path)


if __name__ == "__main__":
    main()
