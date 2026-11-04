from app.source import _decode_abstract


def test_decode_openalex_abstract():
    assert _decode_abstract({"science": [2], "Open": [0], "data": [1]}) == "Open data science"


def test_decode_empty():
    assert _decode_abstract(None) is None
