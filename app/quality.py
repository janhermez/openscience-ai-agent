from app.models import QualityIssue, QualityReport, Work


def evaluate(work: Work) -> QualityReport:
    """Rule-based *demonstration*, not authoritative bibliographic validation."""
    issues: list[QualityIssue] = []
    penalties = 0
    checks = [
        (not (work.title or "").strip(), "missing_title", "critical", "Brak tytułu", 30),
        (not work.authors, "missing_authors", "warning", "Brak autorów", 20),
        (work.publication_year is None, "missing_year", "warning", "Brak roku publikacji", 20),
        (not (work.doi or "").strip(), "missing_doi", "info", "Brak DOI (nie zawsze wymagany)", 15),
        (not (work.abstract or "").strip(), "missing_abstract", "info", "Brak abstraktu (nie zawsze wymagany)", 15),
    ]
    for failed, code, severity, message, cost in checks:
        if failed:
            issues.append(QualityIssue(code=code, severity=severity, message=message))
            penalties += cost
    return QualityReport(work_id=work.id, score=max(0, 100 - penalties), issues=issues)
