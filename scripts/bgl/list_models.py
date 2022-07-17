"""
List all scenery object models defined in a .bgl file
"""

import glob
import logging
import sys
from typing import List

from fs_parse.bgl.classes import BGLFile
from fs_parse.utils import configure_logging


def main():
    if len(sys.argv) <= 1:
        print(f"Usage: {sys.argv[0]} path_to_bgl")
        sys.exit(1)
    configure_logging(logging.INFO)
    file_paths: List[str] = glob.glob(sys.argv[1], recursive=True)
    total_files_count = len(file_paths)
    print(f"Analyzing {total_files_count} files")
    for i, file_path in enumerate(file_paths, start=1):
        print()
        print(f"[{i}/{total_files_count}] {file_path}")
        bgl_file = BGLFile.from_file(file_path)
        for model in bgl_file.get_models():
            print(model.uuid)


if __name__ == '__main__':
    main()
