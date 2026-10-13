"""Interface to EndNote."""

import time
from collections.abc import Iterable
from pathlib import Path

import click
from defusedxml import ElementTree

from citation_url import group


def process_endnote_xml(path: str | Path) -> dict[str, set[str]]:
    """Extract all URLs from an EndNote XML file."""
    tree = ElementTree.parse(path)
    urls = (
        element.text
        for query in ("text-urls", "pdf-urls")
        for element in tree.findall(f"records/record/urls/{query}/url")
        if element.text is not None and element.text.startswith("http")
    )
    groups = group(urls, keep_none=False)
    groups.setdefault("doi", set()).update(
        element.text
        for element in tree.findall("records/record/electronic-resource-num")
        if element.text
    )
    return groups


def endnote_to_wikidata(path: str | Path) -> None:
    """Ensure the contents of the EndNote XML file are added to Wikidata."""
    groups = process_endnote_xml(path=path)
    _upload_wikidata(
        id_type="pmcid",
        source="europepmc",
        identifiers=[x.removeprefix("PMC") for x in groups.get("pmc", [])],
    )
    _upload_wikidata(id_type="doi", source="crossref", identifiers=groups.get("doi", []))
    _upload_wikidata(id_type="pmid", source="europepmc", identifiers=groups.get("pubmed", []))
    _upload_wikidata(id_type="arxiv", source="arxiv", identifiers=groups.get("arxiv", []))
    _upload_wikidata(id_type="biorxiv", source="biorxiv", identifiers=groups.get("biorxiv", []))


def _upload_wikidata(id_type: str, source: str, identifiers: Iterable[str]) -> None:
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
        except Exception as e:  # noqa:BLE001
            tqdm.write(f"{id_type}:{identifier}")
            tqdm.write(f"    failure: {e}")


@click.command()
@click.argument("path", type=click.Path(path_type=Path))
def main(path: Path) -> None:
    """Ensure the papers in a EndNote XML are added to Wikidata."""
    endnote_to_wikidata(path)


if __name__ == "__main__":
    main()
