from datetime import date, datetime
from src.core.models import AcademicRecord

# import json
from dataclasses import asdict
import requests

BASE_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"


def search_europe_pmc(
    query: str,
    limit_date: str = "",
    page_size: int = 500,
) -> list[dict]:
    current_date = date.today().isoformat()

    url_query = (
        f"({query}) "
        f"HAS_FREE_FULLTEXT:Y "
        f"FIRST_PDATE:[{limit_date}-01-01 TO {current_date}]"
    )

    params = {
        "query": url_query,
        "format": "json",
        "resultType": "core",
        "synonym": "TRUE",
        "cursorMark": "*",
        "sort": "PUB_YEAR desc",
        "pageSize": page_size,
    }

    resp = requests.get(
        BASE_URL,
        params=params,
        timeout=300,
    )

    resp.raise_for_status()

    return resp.json()["resultList"]["result"]


def get_record_source(data) -> str | None:
    if data.get("journalInfo", {}).get("journal", {}).get("title", ""):
        return data.get("journalInfo", {}).get("journal", {}).get("title", "")
    elif data.get("bookOrReportDetails", {}).get("publisher", ""):
        return data.get("bookOrReportDetails", {}).get("publisher", "")
    else:
        return None


def get_best_url(data) -> str | None:
    priority = ["pdf", "html", "doi"]

    urls = data.get("fullTextUrlList", {}).get("fullTextUrl", [])

    for document_style in priority:
        for item in urls:
            if (
                item.get("availabilityCode") in ("OA", "F")
                and item.get("documentStyle") == document_style
            ):
                return item.get("url")

    return None


def get_doc_type_string(data) -> str | None:
    input_type_list = data.get("pubTypeList", {})

    types = input_type_list.get("pubType", [])
    types = (t.lower() for t in types)

    return "|".join(types)


def get_publication_date(data) -> date | None:
    pub_date = data.get("firstPublicationDate", "")
    return datetime.strptime(pub_date, "%Y-%m-%d").date()


def json_default(obj):
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    return asdict(obj)


def format_output(result_list: list[dict]) -> list[AcademicRecord]:
    records = []

    for result in result_list:
        record = {
            "source": get_record_source(result),
            "doi": result.get("doi"),
            "title": result.get("title"),
            "abstract": result.get("abstractText"),
            "authors": result.get("authorString"),
            "pub_date": get_publication_date(result),
            "pdf_url": get_best_url(result),
            "doc_type": get_doc_type_string(result),
        }

        records.append(AcademicRecord(**record))

    # with open("records_europe_pmc.json", "w", encoding="utf-8") as file:
    #     json.dump(records, file, default=json_default, indent=4, ensure_ascii=False)

    return records
