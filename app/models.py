from pydantic import BaseModel, Field


class Work(BaseModel):
    id: str
    title: str | None = None
    publication_year: int | None = None
    doi: str | None = None
    authors: list[str] = Field(default_factory=list)
    abstract: str | None = None
    source: str = "manual"
    url: str | None = None


class QualityIssue(BaseModel):
    code: str
    severity: str
    message: str


class QualityReport(BaseModel):
    work_id: str
    score: int
    issues: list[QualityIssue]
    note: str = "Wynik heurystyczny; zależy od typu publikacji i wymaga walidacji eksperckiej."


class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=1200)
