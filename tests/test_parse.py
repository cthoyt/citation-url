"""Tests for parsing."""

import unittest

import citation_url
from citation_url import PREFIXES, PROTOCOLS, Result, Status


class TestParse(unittest.TestCase):
    """Tests for parsing."""

    def test_protocols(self):
        """Test all protocols are formed properly."""
        for protocol in PROTOCOLS:
            with self.subTest(protocol=protocol):
                self.assertTrue(protocol.endswith("://"))

    def test_prefixes(self):
        """Test no prefixes include protocols."""
        for prefix in PREFIXES:
            with self.subTest(prefix=prefix):
                self.assertFalse(any(prefix.startswith(protocol) for protocol in PROTOCOLS))

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
        ]
        for url in data:
            with self.subTest(url=url):
                self.assertEqual(Result(Status.irreconcilable, None, url), citation_url.parse(url))
