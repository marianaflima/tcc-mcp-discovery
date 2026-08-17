from pyalex import Works
from src.core.models import AcademicRecord

# import os
# import pyalex
# from dotenv import load_dotenv

# load_dotenv()

# pyalex.config.api_key = os.getenv("OPENALEX_API_KEY")

def search_open_alex(search_string: str, initial_year: int) -> list[dict]:

    response = (
        Works()
        .search(f"{search_string}")
        .filter(is_oa=True, publication_year=f">{initial_year}")
        .get()
    )

    return response

def get_authors(data) -> str | None:
    authors_list = data.get("authorships", [])

    authors = [a.get("raw_author_name") for a in authors_list]

    return ", ".join(authors)

def get_main_source(data) -> str | None:
    return data.get("primary_location").get("raw_source_name")

def format_output(result_list: list[dict]) -> list[AcademicRecord]:
    records = []

    for result in result_list:
        record = {
            "source": get_main_source(result),
            "doi": result.get("doi", ""),
            "title": result.get("title", ""),
            "abstract": result.get("abstract", ""),
            "authors": get_authors(result),
            "pub_date": result.get("publication_date", ""),
            "pdf_url": result.get("primary_location", {}).get("pdf_url", ""),
            "doc_type": result.get("type", ""),
        }
