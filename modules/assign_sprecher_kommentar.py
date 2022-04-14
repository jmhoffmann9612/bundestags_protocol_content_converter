import re
from warnings import warn

from modules.utilities import balanced_brackets

from modules.constants import ROLES_LIST_REGEX, OFFSET_AFTER_IVZ, MAY_BE_SPEAKER_REGEX


def assign_sprecher_kommentar(pages, tops, sprecher_list):

    # sprecher_list as regex
    SPRECHER_REGEX = "|".join([re.escape(x) for x in sprecher_list])
    # sprecher_list without roles/parties
    SPRECHER_LIST_NO_ROLES = [y.split("(")[0].strip() for y in [re.sub(
        ROLES_LIST_REGEX, "", x).replace(", ", "") for x in sprecher_list]]
    SPRECHER_LIST_NO_ROLES_PARTY_REGEX = "|".join(
        [re.escape(x) for x in SPRECHER_LIST_NO_ROLES])
    # tops as regex
    TOPS_LIST = [x['titel'] for x in tops]
    TOPS_REGEX = "|".join([re.escape(x) for x in TOPS_LIST])
    zusatz_top_list = [x['titel'] for x in tops if x['is_zusatztop']]
    zusatz_top_list = [re.sub(r"Antrag.+?:", r"", x).strip()
                       for x in zusatz_top_list]
    zusatz_top_list = [re.sub(r"\(.+?\)", r"", x).strip()
                       for x in zusatz_top_list]
    ZUSATZ_TOP_LIST = [re.sub(r"\uf020", r"", x).strip()
                       for x in zusatz_top_list]
    ZUSATZ_TOP_LIST_DRUCKSACHEN = [x['drucksache']
                                   for x in tops if x['is_zusatztop']]
    ZUSATZ_TOP_REGEX = "|".join([re.escape(x) for x in ZUSATZ_TOP_LIST])
    ZUSATZ_TOP_REGEX_DRUCKSACHEN = "|".join(
        [re.escape(x) for x in ZUSATZ_TOP_LIST_DRUCKSACHEN])
    ZUSATZ_TOP_NUMS = [x['zusatztop_num'] for x in tops if x['is_zusatztop']]

    # initialize aktueller_sprecher
    aktueller_sprecher = None
    el_dicts = []
    for i, page in enumerate(pages):
        current_page = i + OFFSET_AFTER_IVZ + 1
        for j, el in enumerate(page):
            el_dict = {'sprecher': None, 'text': None,
                       'page': current_page, 'top': None}
            txt = " ".join(el.get_text().split())
            txt = txt.replace("- ", "")

            # check for sprecher at start of txt
            re_match_sprecher = re.match(r"(" + SPRECHER_REGEX + r"):", txt)
            # check without roles/parties
            re_match_sprecher_no_roles_party = re.match(
                r"("+SPRECHER_LIST_NO_ROLES_PARTY_REGEX+r")", txt)
            if re_match_sprecher:
                aktueller_sprecher = re_match_sprecher.group(1)
                txt = txt.replace(aktueller_sprecher + ":", "")
                txt = txt.strip()
            # if line is split with - at end, check for just the name without roles
            elif txt.endswith("-"):
                if re_match_sprecher_no_roles_party:
                    aktueller_sprecher = sprecher_list[SPRECHER_LIST_NO_ROLES.index(
                        re_match_sprecher_no_roles_party.group(1))]
            elif re_match_sprecher_no_roles_party:
                # lookahead two lines until a sprecher is found
                # very hacky, but works
                # finds sprecher if separated by a line break and text is justified
                # fails if elements were not properly ordered in previous step (see 18002, Konstantin von Notz)
                try:
                    txt_lookahead_1 = " ".join(page[j+1].get_text().split())
                    txt_lookahead_1 = txt_lookahead_1.replace("- ", "")
                    txt_lookahead_2 = " ".join(page[j+2].get_text().split())
                    txt_lookahead_2 = txt_lookahead_2.replace("- ", "")
                    txt_lookahead = txt + " " + txt_lookahead_1 + " " + txt_lookahead_2
                    re_match_sprecher = re.match(
                        r"(" + SPRECHER_REGEX + r"):", txt_lookahead)
                    if re_match_sprecher:
                        aktueller_sprecher = re_match_sprecher.group(1)
                        txt = txt.replace(aktueller_sprecher + ":", "")
                        txt = txt.strip()
                except IndexError:
                    pass

            el_dict['text'] = txt
            # if starts and ends with (), then kommentar
            if txt.startswith("(") and txt.endswith(")"):
                el_dict['sprecher'] = "KOMMENTAR"
            else:
                el_dict['sprecher'] = aktueller_sprecher
            el_dicts.append(el_dict)

    # concat with same sprecher and page
    el_dicts_concat = []
    for el_dict in el_dicts:
        if el_dicts_concat:
            last_el_dict = el_dicts_concat[-1]
            if last_el_dict['sprecher'] == el_dict['sprecher'] and last_el_dict['page'] == el_dict['page']:
                last_el_dict['text'] += " " + el_dict['text']
            else:
                el_dicts_concat.append(el_dict)
        else:
            el_dicts_concat.append(el_dict)

    for el_dict in el_dicts_concat:
        el_dict['text'] = " ".join(el_dict['text'].split())
        el_dict['text'] = el_dict['text'].replace("- ", "")

    # split at tops, repeat this until no more changes

    def get_el_dicts_with_tops(base_dict):
        el_dicts_with_tops = []
        for el_dict in base_dict:
            text_no_invalid = el_dict['text'].replace(
                '\uf020', '')  # unicode for invalid character
            if text_no_invalid in TOPS_LIST:
                el_dicts_with_tops.append(el_dict)
                continue

            top_in_text = re.search(TOPS_REGEX, text_no_invalid)
            zusatz_top_in_text = re.search(r"("+ZUSATZ_TOP_REGEX+r")" + r" \u2013 " +
                                           r"Drucksache ("+ZUSATZ_TOP_REGEX_DRUCKSACHEN+r")", text_no_invalid)
            if top_in_text:
                top_str = top_in_text.group(0)
                split_by_top = text_no_invalid.split(top_str)

                up_to_top = el_dict.copy()
                up_to_top['text'] = split_by_top[0].strip()

                top = el_dict.copy()
                top['text'] = top_str.strip()

                after_top = el_dict.copy()
                after_top['text'] = split_by_top[1].strip()

                el_dicts_with_tops.append(up_to_top)
                el_dicts_with_tops.append(top)
                el_dicts_with_tops.append(after_top)
            elif zusatz_top_in_text:
                top_str = zusatz_top_in_text.group(0)
                split_by_top = text_no_invalid.split(top_str)

                up_to_top = el_dict.copy()
                up_to_top['text'] = split_by_top[0].strip()

                top = el_dict.copy()
                top_ds = el_dict.copy()
                top['text'] = zusatz_top_in_text.group(1).strip()
                top_ds['text'] = "Drucksache " + \
                    zusatz_top_in_text.group(2).strip()

                after_top = el_dict.copy()
                after_top['text'] = split_by_top[1].strip()

                el_dicts_with_tops.append(up_to_top)
                el_dicts_with_tops.append(top)
                el_dicts_with_tops.append(after_top)
            else:
                el_dicts_with_tops.append(el_dict)
        return el_dicts_with_tops

    el_dicts_with_tops = get_el_dicts_with_tops(el_dicts_concat)
    while True:
        el_dicts_with_tops_old = el_dicts_with_tops.copy()
        el_dicts_with_tops = get_el_dicts_with_tops(el_dicts_with_tops)
        if el_dicts_with_tops == el_dicts_with_tops_old:
            break

    # assign tops
    aktueller_top = min([int(x['num']) for x in tops if x is not None])
    for el_dict in el_dicts_with_tops:
        txt = el_dict['text']
        if txt in TOPS_LIST:
            aktueller_top = tops[TOPS_LIST.index(txt)]['num']
        elif txt in ZUSATZ_TOP_LIST:
            aktueller_top = "z" + ZUSATZ_TOP_NUMS[ZUSATZ_TOP_LIST.index(txt)]
        el_dict['top'] = aktueller_top

    # cleanup
    # check for unbalanced brackets (page broken kommentare)
    unbalanced_brackets_dict_queue = []
    el_dicts_unbalanced_brackets_fixed = []
    for el_dict in el_dicts_with_tops:
        if not balanced_brackets(el_dict['text']):
            if not unbalanced_brackets_dict_queue:
                unbalanced_brackets_dict_queue.append(el_dict)
            else:
                unbalanced_brackets_dict_queue.append(el_dict)
                base_d = unbalanced_brackets_dict_queue[0].copy()
                for d in unbalanced_brackets_dict_queue[1:]:
                    base_d['text'] += " " + d['text']
                komm = re.search(r"\((.*?)\)", base_d['text']).group(0)
                txt = base_d['text'].split(komm)
                up_to_komm = base_d.copy()
                up_to_komm['text'] = txt[0].strip()
                komm_dict = base_d.copy()
                komm_dict['sprecher'] = "KOMMENTAR"
                komm_dict['text'] = komm.strip()
                after_komm = base_d.copy()
                after_komm['text'] = txt[1].strip()

                if up_to_komm['text']:
                    el_dicts_unbalanced_brackets_fixed.append(up_to_komm)
                el_dicts_unbalanced_brackets_fixed.append(komm_dict)
                if after_komm['text']:
                    el_dicts_unbalanced_brackets_fixed.append(after_komm)

                unbalanced_brackets_dict_queue = []
        elif unbalanced_brackets_dict_queue:
            unbalanced_brackets_dict_queue.append(el_dict)
        else:
            el_dicts_unbalanced_brackets_fixed.append(el_dict)

    # check and fix for speeches nested in other text
    el_dicts_fixed_sprecher = []
    for el_dict in el_dicts_unbalanced_brackets_fixed:
        if el_dict['sprecher'] == "KOMMENTAR" or el_dict['sprecher'] is None:
            el_dicts_fixed_sprecher.append(el_dict)
            continue
        nested_sprecher = re.search(SPRECHER_REGEX, el_dict['text'])
        if nested_sprecher:
            nested_sprecher_txt = nested_sprecher.group(0)
            base_d = el_dict.copy()
            split_txt = base_d['text'].split(nested_sprecher_txt)
            before_split = base_d.copy()
            before_split['text'] = split_txt[0].strip()
            after_split = base_d.copy()
            after_split['sprecher'] = nested_sprecher_txt.strip()
            after_split['text'] = split_txt[1].lstrip(": ").strip()
            el_dicts_fixed_sprecher.append(before_split)
            el_dicts_fixed_sprecher.append(after_split)
        else:
            el_dicts_fixed_sprecher.append(el_dict)

    # remove sprecher at start of text (happens on page breaks)
    for el_dict in el_dicts_fixed_sprecher:
        if el_dict['sprecher'] is not None:
            if el_dict['text'].startswith(el_dict['sprecher']):
                el_dict['text'] = el_dict['text'].replace(
                    el_dict['sprecher'], "")
                el_dict['text'] = el_dict['text'].strip()
            sprecher_no_party = el_dict['sprecher'].split("(")[0].strip()
            if el_dict['text'].startswith(sprecher_no_party):
                el_dict['text'] = el_dict['text'].replace(
                    sprecher_no_party, "")
                el_dict['text'] = el_dict['text'].strip()
            # also try placing comma separated role at start of sprecher
            sprecher_comma_role_first = el_dict['sprecher'].split(",")
            if len(sprecher_comma_role_first) > 1:
                # special case ministers:
                if "Bundesministerin" in sprecher_comma_role_first[1]:
                    sprecher_comma_role_first[1] = "Bundesministerin"
                elif "Bundesminister" in sprecher_comma_role_first[1]:
                    sprecher_comma_role_first[1] = "Bundesminister"
                sprecher_comma_role_first = sprecher_comma_role_first[1].strip(
                ) + " " + sprecher_comma_role_first[0].strip()
                if el_dict['text'].startswith(sprecher_comma_role_first):
                    el_dict['text'] = el_dict['text'].replace(
                        sprecher_comma_role_first, "")
                    el_dict['text'] = el_dict['text'].strip()

    # yeet empty text
    el_dicts_no_empty = []
    for el_dict in el_dicts_fixed_sprecher:
        if el_dict['text']:
            el_dicts_no_empty.append(el_dict)

    # warn about potential speakers nested in text
    for i, el_dict in enumerate(el_dicts_no_empty):
        s = re.match(MAY_BE_SPEAKER_REGEX, el_dict['text'])
        if s:
            warn("Potential speaker found in text.")
            print(el_dict['text'])
            print(s)
            print()
    return el_dicts_no_empty
