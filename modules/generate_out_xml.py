import re
import xml.etree.ElementTree as ET

from modules.utilities import unique_elements

from modules.constants import ROLES_LIST_REGEX, REGEX_BEGINN, REGEX_SCHLUSS, MISSING_FROM_STAMMDATEN


def generate_out_xml(json_data, sprecher, mdb_inverted_index, mdb_relevant_data, file_id):

    wahlperiode = file_id[:2]
    sitzungsnummer = file_id[2:]

    sprecher_id_dict = {}
    for x in sprecher:
        s = x.split("(")[0].strip()
        s = s.replace(",", "")
        s = " ".join(s.split())
        s = re.sub(ROLES_LIST_REGEX, "", s).strip()
        if s in MISSING_FROM_STAMMDATEN:
            sprecher_id_dict[x] = None
            continue
        try:
            sprecher_id_dict[x] = mdb_inverted_index[s]
        except KeyError:
            for key in mdb_inverted_index:
                if s in key:
                    sprecher_id_dict[x] = mdb_inverted_index[key]
                    break

    try:
        assert len(sprecher_id_dict) == len(
            sprecher), "not all sprecher had an id assigned"
    except AssertionError:
        print(f"length sprecher_id_dict: {len(sprecher_id_dict)}")
        print(f"length sprecher: {len(sprecher)}")
        print(
            f"Unmatched: {unique_elements(sprecher_id_dict.keys(), sprecher)}")
        raise

    root = ET.Element("sitzungsverlauf")
    data = json_data.copy()
    header = data.pop(0)
    beginn = re.search(REGEX_BEGINN, header['text']).group(1).replace(".", ":")
    el_sitzungsbeginn = ET.SubElement(
        root, "sitzungsbeginn", {"sitzung-start-uhrzeit": beginn})
    # page 1 info
    ET.SubElement(el_sitzungsbeginn, "a", {
                  "id": "S1", "name": "S1", "typ": "druckseitennummer"})

    current_page = 1
    current_top = None
    current_sprecher = None
    # track next top
    next_top_index = 0
    # list of uniques, preserving order
    tops = list(dict.fromkeys([x['top'] for x in data]))
    tops.append(None)  # avoid index out of range
    current_speech_index = 0
    for el_dict in data:
        if el_dict['sprecher'] == "KOMMENTAR":
            el_komm = ET.SubElement(el_rede, "kommentar")
            el_komm.text = el_dict['text']
            continue
        if str(el_dict['top']) == str(tops[next_top_index]) and el_dict['sprecher'] is None:
            next_top_index += 1
            # do not cast this as str here, this breaks the code
            current_top = el_dict['top']
            if str(current_top).startswith("z"):
                el_current_top = ET.SubElement(root, "tagesordnungspunkt", {
                    "top-id": "Zusatztagesordnungspunkt " + str(current_top)[1:]})
            else:
                el_current_top = ET.SubElement(root, "tagesordnungspunkt", {
                    "top-id": "Tagesordnungspunkt " + str(current_top)})
        elif str(el_dict['top']) == str(tops[next_top_index]):
            next_top_index += 1
            current_top = el_dict['top']  # see above
            # DUPLICATE WITH BELOW
            current_sprecher = el_dict['sprecher']
            if str(current_top).startswith("z"):
                el_current_top = ET.SubElement(root, "tagesordnungspunkt", {
                    "top-id": "Zusatztagesordnungspunkt " + str(current_top)[1:]})
            else:
                el_current_top = ET.SubElement(root, "tagesordnungspunkt", {
                    "top-id": "Tagesordnungspunkt " + str(current_top)})
            current_speech_index += 1
            el_rede = ET.SubElement(
                el_current_top, "rede", {'id': f"ID{wahlperiode}{sitzungsnummer}{current_speech_index:02d}00"})
            el_redner = ET.SubElement(el_rede, "p", {'klasse': 'redner'})
            redner_id = sprecher_id_dict[current_sprecher]
            if redner_id is not None:
                redner_info = mdb_relevant_data[redner_id]
                el_redner_detail = ET.SubElement(
                    el_redner, "redner", {'id': str(redner_id)})
                el_name = ET.SubElement(el_redner_detail, "name")
                if redner_info['anrede_titel']:
                    el_titel = ET.SubElement(el_name, "titel")
                    el_titel.text = redner_info['anrede_titel']
                el_vorname = ET.SubElement(el_name, "vorname")
                el_vorname.text = redner_info['vorname']
                el_nachname = ET.SubElement(el_name, "nachname")
                el_nachname.text = redner_info['nachname']
                if redner_info['ortszusatz']:
                    el_ortszusatz = ET.SubElement(el_name, "ortszusatz")
                    el_ortszusatz.text = redner_info['ortszusatz']
                party_suffix = re.findall(r"\((.+?)\)", current_sprecher)
                if party_suffix:
                    el_fraktion = ET.SubElement(el_name, "fraktion")
                    el_fraktion.text = party_suffix[-1]

                rolle = re.match(ROLES_LIST_REGEX, current_sprecher)
                if rolle:
                    el_name.remove(el_titel) if el_titel in el_name else None
                    el_rolle = ET.SubElement(el_name, "rolle")
                    el_rolle_lang = ET.SubElement(el_rolle, "rolle_lang")
                    el_rolle_lang.text = rolle.group(0)
                    el_rolle_kurz = ET.SubElement(el_rolle, "rolle_kurz")
                    el_rolle_kurz.text = rolle.group(0)
                    if redner_info['anrede_titel']:
                        el_vorname.text = redner_info['anrede_titel'] + \
                            " " + el_vorname.text
                    # TODO: maybe rolle in nachname
                    el_vorname.text = rolle.group(0) + " " + el_vorname.text

            el_redner_detail.tail = current_sprecher + ":"
            # DUPLICATE END

        if el_dict['sprecher'] != current_sprecher and el_dict['sprecher'] != "KOMMENTAR":
            # DUPLICATE WITH ABOVE
            current_sprecher = el_dict['sprecher']
            # el_current_top = ET.SubElement(root, "tagesordnungspunkt", {"top-id": str(current_top)})
            current_speech_index += 1
            el_rede = ET.SubElement(
                el_current_top, "rede", {'id': f"ID{wahlperiode}{sitzungsnummer}{current_speech_index:02d}00"})  # TODO: id
            el_redner = ET.SubElement(el_rede, "p", {'klasse': 'redner'})
            redner_id = sprecher_id_dict[current_sprecher]
            el_redner_detail = ET.SubElement(
                el_redner, "redner", {'id': str(redner_id)})
            if redner_id is not None:
                redner_info = mdb_relevant_data[redner_id]
                el_name = ET.SubElement(el_redner_detail, "name")
                if redner_info['anrede_titel']:
                    el_titel = ET.SubElement(el_name, "titel")
                    el_titel.text = redner_info['anrede_titel']
                el_vorname = ET.SubElement(el_name, "vorname")
                el_vorname.text = redner_info['vorname']
                if redner_info['praefix']:
                    el_namenszusatz = ET.SubElement(el_name, "namenszusatz")
                    el_namenszusatz.text = redner_info['praefix']
                el_nachname = ET.SubElement(el_name, "nachname")
                el_nachname.text = redner_info['nachname']
                if redner_info['ortszusatz']:
                    el_ortszusatz = ET.SubElement(el_name, "ortszusatz")
                    el_ortszusatz.text = redner_info['ortszusatz']
                party_suffix = re.findall(r"\((.+?)\)", current_sprecher)
                if party_suffix:
                    el_fraktion = ET.SubElement(el_name, "fraktion")
                    el_fraktion.text = party_suffix[-1]

                rolle = re.match(ROLES_LIST_REGEX, current_sprecher)
                if rolle:
                    el_name.remove(el_titel) if el_titel in el_name else None
                    el_rolle = ET.SubElement(el_name, "rolle")
                    el_rolle_lang = ET.SubElement(el_rolle, "rolle_lang")
                    el_rolle_lang.text = rolle.group(0)
                    el_rolle_kurz = ET.SubElement(el_rolle, "rolle_kurz")
                    el_rolle_kurz.text = rolle.group(0)
                    if redner_info['anrede_titel']:
                        el_vorname.text = redner_info['anrede_titel'] + \
                            " " + el_vorname.text
                    # TODO: maybe rolle in nachname
                    el_vorname.text = rolle.group(0) + " " + el_vorname.text

            el_redner_detail.tail = current_sprecher + ":"
            # DUPLICATE END

        ET.SubElement(el_rede, "p").text = el_dict['text']  # TODO? Klasse
        # if different page, add info to last element in el_rede
        if el_dict['page'] != current_page:
            last_el = el_rede[-1]
            ET.SubElement(last_el, "a", {
                          "id": "S" + str(el_dict['page']), "name": "S" + str(el_dict['page']), "typ": "druckseitennummer"})
            current_page = el_dict['page']
    # TODO: sitzungsende
    # find last kommentar in json data
    last_kommentar = None
    for el in reversed(json_data):
        if el['sprecher'] == "KOMMENTAR":
            last_kommentar = el
            break

    schluss = re.search(REGEX_SCHLUSS, last_kommentar['text']).group(
        1).replace(".", ":")
    ET.SubElement(root, "sitzungsende", {"sitzung-ende-uhrzeit": schluss})
    return root
