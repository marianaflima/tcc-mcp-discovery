from dataclasses import dataclass, field
from datetime import date

@dataclass
class AcademicRecord:
    source: str
    doi: str | None
    title: str
    abstract: str
    authors: str
    pub_date: date | None
    pdf_url: str | None
    doc_type: str | None