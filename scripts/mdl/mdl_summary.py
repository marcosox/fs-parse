"""
List all sections from an MDL file in hierarchical order
"""
import glob
import logging
import sys
from typing import List

from fs_parse.mdl.classes import MDLSection
from fs_parse.mdl.main_classes import MDLFile
from fs_parse.utils import configure_logging

logger = logging.getLogger(__name__)


def main():
    if len(sys.argv) <= 1:
        print(f"Usage: {sys.argv[0]} path_to_mdl")
        sys.exit(1)
    configure_logging(level=logging.INFO)

    file_paths: List[str] = glob.glob(sys.argv[1], recursive=True)
    total_files_count = len(file_paths)
    for i, file_path in enumerate(file_paths, start=1):
        print(f"[{i}/{total_files_count}] {file_path}")
        mdl_file: MDLFile = MDLFile.from_file(file_path)
        for section in [v for k, v in mdl_file.riff_section.to_dict().items() if isinstance(v, MDLSection) and k != "MDLD"]:
            print(f"\t{section}")
        print("MDLD sections:")
        for section in [v for k, v in mdl_file.riff_section.mdld.to_dict().items() if isinstance(v, MDLSection)]:
            print(f"\t\t{section}")


if __name__ == '__main__':
    main()
