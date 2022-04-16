RECURSION_LIMIT = 100000

# TODO: below values must be set programmatically, as they may differ even for the same Wahlperiode
PAGE_WIDTH = 612
PAGE_HEIGHT = 859
IS_PAGE_IF_SPAN_CONTAINS = f"width:{str(PAGE_WIDTH)}px; height:{str(PAGE_HEIGHT)}px;"

LINE_WIDTH = 0
LINE_LEFT = 306
IS_LINE_IF_SPAN_CONTAINS = f"left:{str(LINE_LEFT)}px;.*width:{LINE_WIDTH}px;"

# search for side markers (A), (B), etc
SIDE_MARKER_LEFT_START = 49
SIDE_MARKER_RIGHT_START = 549
RE_SIDE_MARKER_LEFT = f"left:{SIDE_MARKER_LEFT_START}px;"
RE_SIDE_MARKER_RIGHT = f"left:{SIDE_MARKER_RIGHT_START}px;"

# TODO: this does not reset for each file, find a way to get the correct offset
OFFSET_AFTER_IVZ = 0

REGEX_BEGINN = r"Beginn: (\d+\.\d+) Uhr"
REGEX_SCHLUSS = r"Schluss: (\d+.\d+) Uhr"

ROLES_LIST = [
    r"Präsident(?:in)?",
    r"Vizepräsident(?:in)?",
    r"Alterspräsident(?:in)?",
    r"Bundeskanzler(?:in)?",
    r"Bundesminister(?:in)? (.*)",
    r"Staatsminister(?:in)? (.*)",
    r"Parl. Staatssekretär(?:in)? (.*)"
]
ROLES_LIST_REGEX = r"("+'|'.join(ROLES_LIST)+r")"

# regex for finding potential speakers nested in text
MAY_BE_SPEAKER_REGEX = r"(("+'|'.join(ROLES_LIST)+r") (?:.*):)" + \
    r"|(?:(?:.*), Bundesminister(?:in)?(?:.*):)|(?:.* \(.*\):)"

MINISTERS_DICT = {
    "BMI": "des Innern",
    "für Wirtschaft und Energie": "für Wirtschaft und Energie",
    "des Auswärtigen": "des Auswärtigen",
    "des Innern": "des Innern",
    "der Finanzen": "der Finanzen",
    "für Arbeit und Soziales": "für Arbeit und Soziales",
    "für Ernährung und Landwirtschaft": "für Ernährung und Landwirtschaft",
    "der Verteidigung": "der Verteidigung",
    "für Gesundheit": "für Gesundheit",
    "für Verkehr und digitale Infrastruktur": "für Verkehr und digitale Infrastruktur",
    "für Umwelt, Naturschutz, Bau und Reaktorsicherheit": "für Umwelt, Naturschutz, Bau und Reaktorsicherheit",
    "für wirtschaftliche Zusammenarbeit und Entwicklung": "für wirtschaftliche Zusammenarbeit und Entwicklung",
    "für besondere Aufgaben": "für besondere Aufgaben",
    "BMJV": "beim Bundesminister der Justiz und für Verbraucherschutz"
}

EXTRA_SPRECHER = [
    "Dr. Norbert Lammert (CDU/CSU)",
    "Präsident Dr. Norbert Lammert",
    "Vizepräsidentin Edelgard Bulmahn",
    "Heiko Maas, Bundesminister der Justiz und für Verbraucherschutz",
    "Manuela Schwesig, Bundesministerin für Familie, Senioren, Frauen und Jugend",
    "Johanna Wanka, Bundesministerin für Bildung",
    "Vizepräsidentin Ulla Schmidt"
]

MISSING_FROM_STAMMDATEN = [
    "Johanna Wanka",  # missing
    "Manuela Schwesig",  # missing
    "Dr. Diether Dehm",  # under different name 11000365
    "Katrin Göring-Eckardt",  # under different name 11003132
    "Eva Bulling-Schröter"
]
