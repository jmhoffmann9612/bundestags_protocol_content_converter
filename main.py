import os
from bs4 import BeautifulSoup
import json
# import pickle
# import sys  # used to increase recursion limit when pickling
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

### POSSIBLY REQURIED WHEN PICKLING ###
# from modules.constants import RECURSION_LIMIT

# sys.setrecursionlimit(RECURSION_LIMIT)


def pipeline(file_id):

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
    # attempt at pickling pages, attempting to open the pickle will fail with an EOFError
    # try:
    #     with open(f'2_intermediate/ordered_el_lists/bs4_tag_pickle/{file_id}.pickle', 'wb') as f:
    #         pickle.dump(pages, f)
    # except RecursionError as e:
    #     print(e)
    #     print(f'Maximum recursion limit: {sys.getrecursionlimit()}')
    #     print('Try increasing the RECURSION_LIMIT value in modules/constants.py')
    #     raise
    # dump pages text to json
    with open(f"2_intermediate/ordered_el_lists/text_json/{file_id}.json", "w", encoding="utf-8") as f:
        json.dump([[e.get_text() for e in p] for p in pages], f, indent="\t")
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
    files_list = os.listdir('1_input/content_pdf')
    files_list.remove(".gitignore")
    report = {
        'success': [],
        'failure': {
            'NamentlicheAbstimmungNotSupportedError': [],
            'AttributeError': [],
            'TypeError': [],
            'AssertionError': [],
            'ET.ParseError': [],
            'ValueError': []
        }
    }
    for filename in files_list:
        file_id = filename.split('.')[0]
        print(f'---------- Processing {file_id} ----------')
        try:
            pipeline(file_id)
            report['success'].append(file_id)
        except NamentlicheAbstimmungNotSupportedError as e:
            print(e)
            report['failure']['NamentlicheAbstimmungNotSupportedError'].append(
                file_id)
        except AttributeError as e:
            print(e)
            report['failure']['AttributeError'].append(file_id)
        except TypeError as e:
            print(e)
            report['failure']['TypeError'].append(file_id)
        except AssertionError as e:
            print(e)
            report['failure']['AssertionError'].append(file_id)
        except ET.ParseError as e:
            print(e)
            report['failure']['ET.ParseError'].append(file_id)
        except ValueError as e:
            print(e)
            report['failure']['ValueError'].append(file_id)

    # print and dump report
    print(report)
    with open('report.json', 'w', encoding="utf-8") as f:
        json.dump(report, f)


if __name__ == "__main__":
    main()
