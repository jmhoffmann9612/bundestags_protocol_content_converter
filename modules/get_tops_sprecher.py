import re
from warnings import warn

from modules.constants import MINISTERS_DICT, ROLES_LIST_REGEX, EXTRA_SPRECHER


def get_tops(xml_tree):
    xml_root = xml_tree.getroot()
    ivz_blocks = xml_root.findall("inhaltsverzeichnis/ivz-block")

    tops = []

    for ivz_block in ivz_blocks:
        titel = ivz_block.find("ivz-block-titel").text
        if titel.startswith("Tagesordnungspunkt") or titel.startswith("Zusatztagesordnungspunkt"):
            # deliberately set high number as default
            top = {'titel': None, 'sprecher': [], 'num': 9999}
            ivz_eintraege = ivz_block.findall("ivz-eintrag")
            for ivz_eintrag in ivz_eintraege:
                inhalt = ivz_eintrag.find("ivz-eintrag-inhalt")
                if inhalt.find("redner"):
                    top['sprecher'].append(inhalt.find("redner").tail)
                else:
                    top['titel'] = inhalt.text
            if titel.startswith("Zusatztagesordnungspunkt"):
                num = titel.replace("Zusatztagesordnungspunkt ",
                                    "").replace(":", "").strip()
                top['is_zusatztop'] = True
                top['zusatztop_num'] = num
                s = re.search(
                    r"Drucksache (\d+/\d+)", top['titel'])
                if s:
                    top['drucksache'] = s.group(1)
                else:
                    top['drucksache'] = None
            else:
                num = titel.replace("Tagesordnungspunkt ",
                                    "").replace(":", "").strip()
                top['is_zusatztop'] = False
                top['zusatztop_num'] = None
                top['drucksache'] = None
                top['num'] = num
            tops.append(top)
    return tops


def get_sprecher_from_tops(tops):
    sprecher = []
    for top in tops:
        sprecher.extend(top['sprecher'])
    for i, s in enumerate(sprecher):
        s = s.replace('\uf020 ', '')
        s = s.replace(" (zur Geschäftsordnung)", "")
        s = s.replace(" (Erklärung nach § 31 GO)", "")
        search = re.search(ROLES_LIST_REGEX, s)
        if search:
            if search.groups()[1]:
                try:
                    sprecher[i] = sprecher[i].replace(
                        search.groups()[1], MINISTERS_DICT[search.groups()[1]])
                except KeyError:
                    warn(f"{search.groups()[1]} not found in MINISTERS_DICT")
                    print()
        else:
            sprecher[i] = s
    sprecher = list(set(sprecher))
    sprecher.sort()
    return sprecher


def sprecher_speical_rules(sprecher_list):
    # a somewhat nuclear solution to the problem of having speakers (mainly the presidents of parliament) not appear in the table of contents, by adding them manually
    # this is a temporary, and should be replaced by a more robust solution
    l = sprecher_list.copy()
    l.extend(EXTRA_SPRECHER)
    l = list(set(l))
    l.sort()
    return l
