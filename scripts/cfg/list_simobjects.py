"""

"""
import configparser
import glob
import os.path
import re


def main():
    simobjects_dir = "C:\\Program Files (x86)\\Microsoft Games\\Microsoft Flight Simulator X\\SimObjects"
    airplanes_dir = os.path.join(simobjects_dir, "airplanes")
    boats_dir = os.path.join(simobjects_dir, "boats")
    groundvehicles_dir = os.path.join(simobjects_dir, "groundvehicles")
    misc_dir = os.path.join(simobjects_dir, "misc")
    rotorcraft_dir = os.path.join(simobjects_dir, "rotorcraft")

    for folder, filename, outfilename in [
        (airplanes_dir, "aircraft.cfg", "airplanes.txt"),
        (boats_dir, "sim.cfg", "boats.txt"),
        (groundvehicles_dir, "sim.cfg", "groundvehicles.txt"),
        (misc_dir, "sim.cfg", "misc.txt"),
        (rotorcraft_dir, "aircraft.cfg", "rotorcraft.txt"),
    ]:

        result = []
        search_dir = os.path.join(folder, "*", filename)
        for aircraft_cfg_path in glob.glob(search_dir, recursive=True):
            # print(aircraft_cfg_path)
            config = configparser.ConfigParser(comment_prefixes=[";", "#", "//", "\\\\", "--", "=="],
                                               inline_comment_prefixes=["//", "'"],
                                               strict=False,
                                               interpolation=None)
            config.read(aircraft_cfg_path)
            for section in config.sections():
                if re.match("fltsim\\.\\d+", section):
                    item = config.get(section, "title").strip()
                    result.append(str(item.encode("utf-8"), "utf-8"))
                    print(item)

        print(result)
        with open(outfilename, "w") as outfile:
            outfile.write("\n".join(result))
            outfile.write("\n")


if __name__ == '__main__':
    main()
