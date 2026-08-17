import os
# import json
import pyalex
from dataclasses import asdict
from datetime import date, datetime
from dotenv import load_dotenv
from pyalex import Works, OpenAlexResponseList
from src.core.models import AcademicRecord


def setup_open_alex() -> None:
    load_dotenv()

    pyalex.config.api_key = os.getenv("OPENALEX_API_KEY")


def search_open_alex(search_string: str, initial_year: int) -> OpenAlexResponseList:

    response = (
        Works()
        .search(f"{search_string}")
        .filter(is_oa=True, publication_year=f">{initial_year}")
        .get()
    )

    return response


def json_default(obj):
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    return asdict(obj)


def get_authors(data) -> str | None:
    authors_list = data.get("authorships", [])

    authors = [a.get("raw_author_name") for a in authors_list]

    return ", ".join(authors)


def get_abstract_text(data) -> str | None:
    if data.get("abstract_inverted_index") is not None:
        return data["abstract"]
    else:
        return "abstract index not available, try accessing the article if necessary"


def get_main_source(data) -> str | None:
    return data.get("primary_location").get("raw_source_name")


def format_output(result_list: OpenAlexResponseList) -> list[AcademicRecord]:

    records = []

    for result in result_list:
        record = {
            "source": get_main_source(result),
            "doi": result.get("doi", ""),
            "title": result.get("title", ""),
            "abstract": get_abstract_text(result),
            "authors": get_authors(result),
            "pub_date": result.get("publication_date", ""),
            "pdf_url": result.get("primary_location", {}).get("pdf_url", ""),
            "doc_type": result.get("type", ""),
        }

        records.append(AcademicRecord(**record))

    # with open("records_openalex.json", "w", encoding="utf-8") as file:
    #     json.dump(records, file, default=json_default, indent=4, ensure_ascii=False)

    return records

