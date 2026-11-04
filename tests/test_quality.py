from app.models import Work
from app.quality import evaluate


def test_complete_record():
    w = Work(id="a", title="Test", publication_year=2025, doi="10.1234/abc", authors=["A"], abstract="Opis")
    result = evaluate(w)
    assert result.score == 100
    assert result.issues == []


def test_missing_fields():
    w = Work(id="b", title=None)
    result = evaluate(w)
    assert result.score == 0
    assert {issue.code for issue in result.issues} == {"missing_title", "missing_authors", "missing_year", "missing_doi", "missing_abstract"}


def test_missing_doi_is_information_not_fatal():
    w = Work(id="c", title="Test", publication_year=2023, authors=["X"], abstract="Test")
    result = evaluate(w)
    assert result.score == 85
    assert result.issues[0].severity == "info"
