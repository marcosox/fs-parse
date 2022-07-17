"""
Analyze an .mdl file and list its declared textures filenames
"""
import glob
import logging
import sys
from typing import List

from fs_parse.mdl.main_classes import MDLFile
from fs_parse.utils import configure_logging

logger = logging.getLogger(__name__)


def main():
    if len(sys.argv) <= 1:
        print(f"Usage: {sys.argv[0]} path_to_mdl")
        sys.exit(1)
    configure_logging(logging.INFO)
    file_paths: List[str] = glob.glob(sys.argv[1], recursive=True)
    total_files_count = len(file_paths)
    print(f"Analyzing {total_files_count} files")
    result = set()
    for i, file_path in enumerate(file_paths, start=1):
        print()
        print(f"[{i}/{total_files_count}] {file_path}")
        mdl_file = MDLFile.from_file(file_path)
        textures = mdl_file.get_texture_names()
        result = result.union(set(textures))
    print("\n\nTextures:")
    print("\n".join(list(result)))


if __name__ == '__main__':
    main()
