"""
Export all placements defined in a .bgl file to a kml file
"""
import glob
import logging
import os.path
import sys
from typing import List

from simplekml import AltitudeMode, Kml

from fs_parse.bgl.classes import BGLFile
from fs_parse.utils import configure_logging


def main():
    if len(sys.argv) <= 1:
        print(f"Usage: {sys.argv[0]} path_to_bgl")
        sys.exit(1)
    configure_logging(logging.INFO)
    file_paths: List[str] = glob.glob(sys.argv[1], recursive=True)
    total_files_count = len(file_paths)
    print(f"Analyzing {total_files_count} files in {sys.argv[1]}")
    kml = Kml()
    for i, file_path in enumerate(file_paths, start=1):
        print()
        print(f"[{i}/{total_files_count}] {file_path}")
        _, filename = os.path.split(file_path)
        bgl_file = BGLFile.from_file(file_path)
        placements = bgl_file.get_placements()
        if placements:
            folder = kml.newfolder(name=filename)
            for placement in placements:
                is_agl = placement.header.is_above_agl
                altitude_mode = AltitudeMode.relativetoground if is_agl else AltitudeMode.absolute
                point = folder.newpoint(name=placement.obj_info.name, altitudemode=altitude_mode)
                point.coords = [(placement.header.lon, placement.header.lat, placement.header.alt * 0.3048)]
                print("UUID:", placement.obj_info.name)
                print("alt:", placement.header.alt)
                print(" is agl:", placement.header.is_above_agl)
    kml.save("output.kml")


if __name__ == '__main__':
    main()
