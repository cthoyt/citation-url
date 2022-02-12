"""Tests for parsing."""

import unittest
from typing import Iterable

import citation_url
from citation_url import IRRECONCILABLE, PREFIXES, PROTOCOLS, Result, Status


class TestParse(unittest.TestCase):
    """Tests for parsing."""

    def test_protocols(self):
        """Test all protocols are formed properly."""
        for protocol in PROTOCOLS:
            with self.subTest(protocol=protocol):
                self.assertTrue(protocol.endswith("://"))

    def test_prefixes(self):
        """Test no prefixes include protocols."""
        self.help_prefixes(PREFIXES)

    def test_irrec(self):
        """Test no irreconcilable prefixes include protocols."""
        self.help_prefixes(IRRECONCILABLE)

    def help_prefixes(self, prefixes: Iterable[str]):
        """Help test the prefixes don't include protocols."""
        for prefix in prefixes:
            with self.subTest(prefix=prefix):
                self.assertFalse(any(prefix.startswith(protocol) for protocol in PROTOCOLS))

    def test_result_repr(self):
        """Test thee repr of a result."""
        self.assertEqual(
            "Result(status=Status.success, prefix='pubmed', identifier='34739845')",
            repr(Result(status=Status.success, prefix="pubmed", identifier="34739845")),
        )

    def test_parse(self):
        """Test parsing."""
        data = [
            (
                "https://www.biorxiv.org/content/biorxiv/early/2020/03/30/2020.03.27.001834.full.pdf",
                "doi",
                "10.1101/2020.03.27.001834",
            ),
            (
                "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5731347/pdf/MSB-13-954.pdf",
                "pmc",
                "PMC5731347",
            ),
            (
                "10.21105/joss.01708.pdf",
                "doi",
                "10.21105/joss.01708",
            ),
            (
                "https://joss.theoj.org/papers/10.21105/joss.01708.pdf",
                "doi",
                "10.21105/joss.01708",
            ),
            (
                "https://journals.plos.org/ploscompbiol/article/file?id=10.1371/journal.pcbi.1007311&type=printable",
                "doi",
                "10.1371/journal.pcbi.1007311",
            ),
            (
                "https://journals.plos.org/ploscompbiol/article/file?type=printable&id=10.1371/journal.pcbi.1007311",
                "doi",
                "10.1371/journal.pcbi.1007311",
            ),
            (
                "https://elifesciences.org/download/aHR0cHM6Ly9jZG4uZWxpZmV/elife-50036-v1.pdf?_hash=gPY9lWM",
                "doi",
                "10.7554/eLife.50036",
            ),
            (
                "http://www.jbc.org/content/early/2019/03/11/jbc.RA118.006805.full.pdf",
                "doi",
                "10.1074/jbc.RA118.006805",
            ),
            ("https://europepmc.org/articles/pmc4944528?pdf=render", "pmc", "PMC4944528"),
            ("https://europepmc.org/articles/PMC4944528?pdf=render", "pmc", "PMC4944528"),
            ("https://europepmc.org/article/PMC/4944528", "pmc", "PMC4944528"),
            (
                "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi?dbfrom=pubmed&amp;id="
                "27357669&amp;retmode=ref&amp;cmd=prlinks",
                "pubmed",
                "27357669",
            ),
            (
                "https://www.frontiersin.org/articles/10.3389/fphar.2019.00448/pdf",
                "doi",
                "10.3389/fphar.2019.00448",
            ),
            (
                "https://arxiv.org/abs/2006.13365",
                "arxiv",
                "2006.13365",
            ),
            (
                "https://arxiv.org/pdf/2006.13365",
                "arxiv",
                "2006.13365",
            ),
            (
                "https://arxiv.org/pdf/2006.13365.pdf",
                "arxiv",
                "2006.13365",
            ),
        ]
        for url, prefix, identifier in data:
            with self.subTest(url=url):
                self.assertEqual(
                    Result(Status.success, prefix, identifier), citation_url.parse(url)
                )

    def test_unable_to_parse(self):
        """Test URLs that don't have enough information to get a standard identifier."""
        data = [
            "https://www.pnas.org/content/pnas/early/2020/06/24/2000648117.full.pdf",
            "https://www.pnas.org/content/pnas/117/28/16500.full.pdf",
            "https://www.cell.com/article/S245194561930073X/pdf",
            "https://pdfs.semanticscholar.org/91fb/9d1827da26fe87ff232e310ab5b819bbb99f.pdf",
            "http://www.jbc.org/content/294/21/8664.full.pdf",
            "https://www.cell.com/cell-systems/fulltext/S2405-4712(17)30490-8",
            "https://www.cell.com/cell/pdf/S0092-8674(20)30346-9.pdf",
            "http://msb.embopress.org/content/13/11/954.full.pdf",
            "https://msb.embopress.org/content/msb/11/3/797.full.pdf",
        ]
        for url in data:
            with self.subTest(url=url):
                self.assertEqual(Result(Status.irreconcilable, None, url), citation_url.parse(url))
