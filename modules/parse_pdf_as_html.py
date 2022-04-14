import subprocess
import os
import time


def parse_main_as_html(file_id):
    # check if pdf2txt is installed
    in_file_path = f'1_input/content_pdf/{file_id}.pdf'
    out_file_path = f"2_intermediate/html/{file_id}.html"
    if os.path.exists(out_file_path):
        print(f"{out_file_path} already exists")
        return
    try:
        subprocess.run(["pdf2txt.py", "-o", out_file_path,
                       in_file_path], shell=True, check=True)
        # wait for html to be generated
        i = 1
        while not os.path.exists(out_file_path):
            print(f"{file_id}: waiting for html to be generated{i*'.'}",
                  sep='', end='\r')
            i += 1
            time.sleep(1)
        print('')
        print(f"{file_id}: html generated")
    except subprocess.CalledProcessError as e:
        print(f"{file_id}: pdf2txt.py failed")
        print(e)
        print("--- Make sure you have installed pdf2txt.py ---")
        raise
