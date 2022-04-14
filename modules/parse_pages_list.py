import re

from modules.constants import IS_LINE_IF_SPAN_CONTAINS, LINE_LEFT, RE_SIDE_MARKER_LEFT, RE_SIDE_MARKER_RIGHT


def get_vert_lines(pages_lists):
    RE_LINE_START = "top:(\d+)px"
    RE_LINE_LENGTH = "height:(\d+)px"

    vert_lines = []

    for page in pages_lists:
        found = False
        for tag in page:
            style = tag["style"]
            if re.search(IS_LINE_IF_SPAN_CONTAINS, style):
                line_start = int(re.search(RE_LINE_START, style).group(1))
                line_length = int(re.search(RE_LINE_LENGTH, style).group(1))
                found = True
                vert_lines.append((line_start, line_length))
                break
        if not found:
            vert_lines.append((None))
    return vert_lines


def get_pages(pages_lists, vert_lines):
    # per page
    # identify head line and contents above them, as well as side markers and remove them
    # sort elements by top (ordered top to bottom)
    # identify elements left and right of the middle line (if exists) and place right elements after left

    pages = []

    for i, page_els in enumerate(pages_lists):
        # search for head line
        IS_HEAD_LINE_IF_SPAN_CONTAINS = "height:0px;"
        RE_TOP = "top:(\d+)px"
        head_line_top = None
        for el in page_els:
            if re.search(IS_HEAD_LINE_IF_SPAN_CONTAINS, el["style"]):
                head_line_top = int(re.search(RE_TOP, el["style"]).group(1))
        # if head line exists, remove it and everything above
        # also removes the span representing a page, but should not be needed any more anyway
        if head_line_top:
            page_els = [el for el in page_els if int(
                re.search(RE_TOP, el["style"]).group(1)) > head_line_top]

        # search for side markers (A), (B), etc and remove
        page_els = [el for el in page_els if not re.search(
            RE_SIDE_MARKER_LEFT, el["style"])]
        page_els = [el for el in page_els if not re.search(
            RE_SIDE_MARKER_RIGHT, el["style"])]

        # sort elements by top (ordered top to bottom)
        page_els_top = [
            int(re.search("top:(\d+)px;", el["style"]).group(1)) for el in page_els]
        page_els = [x for _, x in sorted(
            zip(page_els_top, page_els), key=lambda pair: pair[0])]

        # identify elements left and right of the middle line (if exists) and place right elements after left
        vert_line = vert_lines[i]
        # tuple (top,width)
        # LINE_LEFT see above
        if vert_line:
            re_el_left = re.compile("left:(\d+)px;")
            left_of_line = [el for el in page_els if int(
                re_el_left.search(el["style"]).group(1)) < LINE_LEFT]
            right_of_line = [el for el in page_els if int(
                re_el_left.search(el["style"]).group(1)) >= LINE_LEFT]
            page_els = list()
            page_els.extend(left_of_line)
            page_els.extend(right_of_line)

        pages.append(page_els)
    return pages
