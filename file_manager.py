import os
import re


def get_files_in_dir_with_ext(src_dir, extension):
    regex = re.compile(f".*.{extension}") # .*.csv
    src_files = []
    for path, _, files in os.walk(src_dir):
        for f in files:
            if regex.match(f):
                src_files.append(os.path.join(path, f))
    return src_files
