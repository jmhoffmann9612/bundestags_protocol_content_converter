import os
from bs4 import BeautifulSoup
import json
import xml.etree.ElementTree as ET

from modules.parse_pdf_as_html import parse_main_as_html
from modules.parse_soup import get_pages_lists
# unused
# from modules.parse_soup import get_page_spans, get_line_spans, get_pages_lists
from modules.parse_pages_list import get_vert_lines, get_pages
from modules.get_tops_sprecher import get_tops, get_sprecher_from_tops, sprecher_speical_rules
from modules.assign_sprecher_kommentar import assign_sprecher_kommentar
from modules.generate_out_xml import generate_out_xml
from modules.custom_exceptions import NamentlicheAbstimmungNotSupportedError

files_list = os.listdir('1_input/content_pdf')
files_list.remove(".gitignore")


def pipeline(filename):
    file_id = filename.split('.')[0]

    # load header data
    with open(f"1_input/toc_xml/{file_id}-vorspann.xml", "r", encoding="utf-8") as f:
        vorspann_tree = ET.parse(f)

    # check if any ivz-eintrag-inhalt.text == "Namentliche Abstimmung" (not supported)
    vorspann_tree_root = vorspann_tree.getroot()
    namentliche_abst = [x.text for x in vorspann_tree_root.findall(
        ".//ivz-eintrag-inhalt") if x.text == "Namentliche Abstimmung"]
    if namentliche_abst:
        raise NamentlicheAbstimmungNotSupportedError(
            f'file_id: {file_id} - Contains "Namentliche Abstimmung", not supported')

    parse_main_as_html(file_id)

    with open(f'2_intermediate/html/{file_id}.html', 'r', encoding="utf-8") as f:
        soup = BeautifulSoup(f, 'html.parser')

    # load mdb data
    with open("mdbs/mdb_inverted_index.json", "r", encoding="utf-8") as f:
        mdb_inverted_index = json.load(f)
    with open("mdbs/mdb_relevant_data.json", "r", encoding="utf-8") as f:
        mdb_relevant_data = json.load(f)

    # unused
    # page_spans = get_page_spans(soup)
    # line_spans = get_line_spans(soup)
    pages_lists = get_pages_lists(soup)
    vert_lines = get_vert_lines(pages_lists)
    pages = get_pages(pages_lists, vert_lines)
    tops = get_tops(vorspann_tree)
    sprecher = get_sprecher_from_tops(tops)
    sprecher = sprecher_speical_rules(sprecher)
    assigned_sprecher = assign_sprecher_kommentar(pages, tops, sprecher)
    with open(f'2_intermediate/json/{file_id}.json', "w", encoding="utf-8") as f:
        # overwrites existing file
        json.dump(assigned_sprecher, f, indent="\t")

    out_xml = generate_out_xml(
        assigned_sprecher, sprecher, mdb_inverted_index, mdb_relevant_data)
    with open("3_output/" + file_id + "-main.xml", "wb") as f:
        f.write('<?xml version="1.0" encoding="UTF-8" ?>\n<!DOCTYPE dbtplenarprotokoll SYSTEM "dbtplenarprotokoll.dtd">\n'.encode('utf8'))
        tree = ET.ElementTree(out_xml)
        ET.indent(out_xml, space="\t", level=0)
        tree.write(f, encoding="utf-8", xml_declaration=False)


def main():
    for filename in files_list:
        try:
            pipeline(filename)
        except NamentlicheAbstimmungNotSupportedError as e:
            print(e)
        except AttributeError as e:
            print(e)
        except TypeError as e:
            print(e)
        except AssertionError as e:
            print(e)
        except ET.ParseError as e:
            print(e)
        except ValueError as e:
            print(e)


if __name__ == "__main__":
    main()
