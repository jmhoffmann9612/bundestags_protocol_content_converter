import re

from modules.constants import IS_PAGE_IF_SPAN_CONTAINS, IS_LINE_IF_SPAN_CONTAINS


def get_page_spans(soup):
    return [item for item in soup.find_all("span") if re.search(IS_PAGE_IF_SPAN_CONTAINS, item["style"])]


def get_line_spans(soup):
    return [item for item in soup.find_all("span") if re.search(IS_LINE_IF_SPAN_CONTAINS, item["style"])]


def get_pages_lists(soup):
    pages_lists = []
    page = []

    for i in soup.body.children:
        if i == "\n":
            continue
        # skip pdf2txt generated page indicators and navigation at top (they have no style attribute "left")
        if not re.search("left:\d+px;", i["style"]):
            continue
        if IS_PAGE_IF_SPAN_CONTAINS in i["style"]:
            if len(page) != 0:
                pages_lists.append(page)
                page = []
        page.append(i)
    pages_lists.append(page)
    return pages_lists
