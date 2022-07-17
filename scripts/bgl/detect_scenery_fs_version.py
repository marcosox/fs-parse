import glob
import logging
import sys
from typing import List, Optional

from fs_parse.bgl.classes import BGLFile
from fs_parse.bgl.constants import BGLSectionType, FSVersion
from fs_parse.bgl.records.sceneryobject import FS9SceneryObjectHeader, FSXSceneryObjectHeader
from fs_parse.bgl.subsections import SceneryObject
from fs_parse.utils import configure_logging


def detect_scenery_file_fs_version(bgl_file: BGLFile) -> Optional[FSVersion]:
    for section in bgl_file.sections:
        if section.section_type == BGLSectionType.SCENERYOBJECT:
            for subsection in section.subsections:
                subsection: SceneryObject
                for record in subsection.records:
                    if isinstance(record.header, FSXSceneryObjectHeader):
                        return FSVersion.FSX
                    elif isinstance(record.header, FS9SceneryObjectHeader):
                        return FSVersion.FS9


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
        print(detect_scenery_file_fs_version(BGLFile.from_file(file_path)))


if __name__ == '__main__':
    main()
