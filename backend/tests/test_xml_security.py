import pytest
from app.validation.xml_utils import parse_xml


def test_rejects_doctype():
    xml = b"""<!DOCTYPE foo [ <!ELEMENT foo ANY > <!ENTITY xxe SYSTEM 'http://example.com/evil'> ]><foo>&xxe;</foo>"""
    with pytest.raises(ValueError):
        parse_xml(xml)


def test_rejects_billion_laughs():
    xml = b"""<!DOCTYPE lolz [
      <!ENTITY lol "lol">
      <!ENTITY lol1 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">
      <!ENTITY lol2 "&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;">
    ]>
    <lolz>&lol2;</lolz>"""
    with pytest.raises(ValueError):
        parse_xml(xml)

