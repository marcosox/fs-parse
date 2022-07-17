"""
List all sections defined in a .bgl file in hierarchical order
"""

import glob
import logging
import sys
from typing import List

from detect_scenery_fs_version import detect_scenery_file_fs_version
from fs_parse.bgl.classes import BGLFile
from fs_parse.bgl.constants import FSVersion
from fs_parse.bgl.records.sceneryobject import FS9LibraryObjectRecord, LibraryObjectRecord
from fs_parse.utils import configure_logging


def print_bgl_info_summary(bgl_file: BGLFile):
    for section in bgl_file.sections:
        print(f"\t{section}")
        for subsection in section.subsections:
            print(f"\t\t{subsection}")
            for record in subsection.records:
                print(f"\t\t\t@0x{record.offset:04x}: {record}")
                if (isinstance(record, LibraryObjectRecord) or isinstance(record, FS9LibraryObjectRecord)) \
                        and record.attached_object:
                    print(f"\t\t\t\t{record.attached_object}")
    detected_fs_version: FSVersion = detect_scenery_file_fs_version(bgl_file)
    if detected_fs_version:
        print("Detected FS version:", detected_fs_version.value)


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
        print(f"{bgl_file}")
        print_bgl_info_summary(bgl_file)


if __name__ == '__main__':
    main()
