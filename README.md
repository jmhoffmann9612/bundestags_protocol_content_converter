# Bundestags protocol content converter

> Note: the script fails for a majority and protocols in its current state. It was also only tested with protocols from the 18. Wahlperiode (2013-2017).

A script for parsing the content of PDF protocols of the German parliament, the Bundestag, older than 2017 into the XML format used to document the more recent Wahlperioden. The definition of this format can be found [here](https://www.bundestag.de/resource/blob/577234/4c8091d8650fe417016bb48e604e3eaf/dbtplenarprotokoll_kommentiert-data.pdf).

All successfully converted documents can be found in the `3_output` directory of this repository.

---

## Prerequisites

- Python 3 (written in version 3.9)
- A Python environment with [PDFminer](https://pypi.org/project/pdfminer) and [beautifulsoup4](https://pypi.org/project/beautifulsoup4/) installed

---

## Repo folder structure

`1_input`: paste input files here

- `content_pdf`: pdf files containing only the content part (no toc and appendix) of each protocol, found [here](https://github.com/Shoggomo/bundestags_protocol_splitter)

- `toc_xml`: xml files containing the parsed toc for each protocol, found [here](https://github.com/Shoggomo/bundestags_protocol_tos_converter/tree/main/xml_output)

`2_intermediate`: content generated by the main script as intermediate steps

- `html`: input pdfs parsed as html

- `json`: html parsed as json, with speakers, text, tops and pages assigned

`3_output`: the finished xml files generated by the main script

`mdbs`: contains parsed data of the German parliament MDBs, as well as the source file and Jupyter notebooks used to generate the data

`mdbs`: modules used by the main script. separated for easier code readability

---

## Usage

Paste the source files in the corresponding input folders (see above), then, with the root folder of this directory as the current working directory, run:

`python main.py`

The script will attempt to parse all files in the input folders and skip generating the finalized XML file, should any script-caused-exceptions be encountered (e.g. the script will still terminate if an input pdf file cannot find corresponding ToC file). HTML and JSON files may still be generated in the `2_intermediate` directory, though their content is usually invalid too, if no XML file was generated.

---

## Parse quality

Note that these were manually tested for only the first 100 out of 245 protocols of the 18. Wahlperiode. Only information on protocols which were skipped because they contained named votes ("Namentliche Abstimmung") is added beyond this.

### Good

- 1, 2, 4

### Bad/skipped

- Skipped (contains Namentliche Abstimmung):
  - 3, 10, 11, 17, 20, 26, 29, 30, 33, 36, 39, 42, 44, 46, 47, 60, 66, 69, 76, 82, 88, 89, 97, 106, 107, 112, 113, 118, 127, 128, 131, 133, 136, 139, 141, 143, 146, 152, 154, 155, 158, 160, 161, 164, 170, 171, 179, 180, 183, 184, 190, 193, 199, 200, 202, 204, 206, 209, 212, 215, 211, 228, 234, 237, 240, 241, 243, 244
- Skipped (pdf2txt.py issues)
  - 5, 15, 48
- Skipped (issue related to Zusatz-TOPs):
  - 7, 8, 12, 13, 14, 19, 21, 22, 23, 24, 25, 32, 35, 43, 45, 53, 54, 56, 57, 63, 65, 70, 72, 73, 75, 78, 79, 81, 87, 90, 91, 92, 93, 94, 99, 100
- Skipped (error in ToC parsing):
  - 9 (zusatz-top assigend incorrectly), 16, 236 (xml not well formed)
- Skipped (other error while parsing):
  - 6, 18, 27, 28, 31, 34, 37, 38, 40, 41, 49, 50, 51, 52, 55, 58, 59, 61, 62, 64, 67, 68, 71, 74, 77, 80, 83, 84, 85, 86, 95, 96, 98

---

## Issues

Unfortunately, the tool only provides good results for a handful of protocols from the 18. Wahlperiode, while failing to produce an XML output for most of them. Here is a list of known issues that are partly the cause for this:

- "Tagesordnungspunkte" with sub-entries are recognized as speakers, leading to an exception being thrown when speakers are not recognized.
- "Drucksachen" (printed material) are not properly recognized (this often leads to the errors related to Zusatz-TOPs mentioned above) and other issues beyond
- pdf2txt.py's html conversion occasionally produces weird results (part of the reason for skipping named votes altogether) and often causes parsing to fail
- Some MDBs are missing from the Stammdaten, or are referred to by more than one name.