"""Tests for parsing."""

import unittest

import citation_url
from citation_url import PREFIXES, PROTOCOLS


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
        ]
        for url, prefix, identifier in data:
            with self.subTest(url=url):
                self.assertEqual((prefix, identifier), citation_url.parse(url))
