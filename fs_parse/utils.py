import glob
import logging
import os
import sys
from typing import List, Optional, Tuple, Union


def parse_longitude(value: int) -> float:
    """
     Convert longitude encoded values to decimal degrees
     see https://www.fsdeveloper.com/wiki/index.php/BGL_File_Format#Computing_Longitude_and_Latitude_from_a_DWORD_value
    """
    return (value * (360.0 / (3 * 0x10000000))) - 180.0


def parse_flags(value: int) -> Tuple[bool, bool, bool, bool, bool, bool, bool]:
    """ Parses 7 boolean flags from a bitmask """
    return (bool(value & 0x0001),
            bool(value & 0x0002),
            bool(value & 0x0004),
            bool(value & 0x0008),
            bool(value & 0x0010),
            bool(value & 0x0020),
            bool(value & 0x0040))


def parse_latitude(value: int) -> float:
    """
     Convert latitude encoded values to decimal degrees
     see https://www.fsdeveloper.com/wiki/index.php/BGL_File_Format#Computing_Longitude_and_Latitude_from_a_DWORD_value
    """
    return 90.0 - value * (180.0 / (2 * 0x10000000))


def parse_pbh_value(value: int) -> float:
    """ Convert a pitch/bank/heading encoded value to decimal degrees """
    return value * 360.0 / 0x10000


def bytes_2_hexstr(buffer: bytes) -> str:
    """ Convert a bytes array into a common hexdump string """
    return " ".join([f"{b:02x}" for b in buffer])


def read_stringz_word_aligned(buffer: bytes) -> Tuple[int, str]:
    """
     Read a bytes buffer to extract a STRINGZ value,
     stopping at the first WORD-aligned offset when reaching 0x00 bytes

     :returns: (raw_size, string) raw_size includes optional trailing 0x00 bytes
    """
    i = 0
    terminated = False
    terminating = False
    result: bytes = bytes()
    while not terminated:
        result += buffer[i:i + 1]
        if buffer[i] == 0x0:
            terminating = True
        if i % 2 == 1 and terminating:
            terminated = True
        i += 1
    rawsize = len(result)
    return rawsize, stringz_2_ascii(result)


def half_float_2_float(float16: int):
    s = int((float16 >> 15) & 0x00000001)  # sign
    e = int((float16 >> 10) & 0x0000001f)  # exponent
    f = int(float16 & 0x000003ff)  # fraction

    if e == 0:
        if f == 0:
            return int(s << 31)
        else:
            while not (f & 0x00000400):
                f = f << 1
                e -= 1
            e += 1
            f &= ~0x00000400
        # print(s,e,f)
    elif e == 31:
        if f == 0:
            return int((s << 31) | 0x7f800000)
        else:
            return int((s << 31) | 0x7f800000 | (f << 13))

    e = e + (127 - 15)
    f = f << 13
    return int((s << 31) | (e << 23) | f)


def read_stringz(buffer: bytes) -> str:
    """
     Read a bytes buffer to extract a zero-terminated string
    """
    i = 0
    terminated = False
    result: bytes = bytes()
    while not terminated:
        result += buffer[i:i + 1]
        if buffer[i] == 0x0:
            terminated = True
        i += 1
    return stringz_2_ascii(result)


def stringz_2_ascii(value: bytes) -> str:
    """ Convert a STRINGZ buffer to a readable string, stripping the trailing 0x00 bytes """
    return str(value, 'ascii').strip('\x00')


def set_bit(value: int, bit: int) -> int:
    """ set the Nth bit to 1 """
    return value | (1 << bit)


def clear_bit(value: int, bit: int) -> int:
    """ set the Nth bit to 0 """
    return value & ~(1 << bit)


def invert_dict(d: dict) -> dict:
    result = {}
    for k, v in d.items():
        result[v] = result.get(v, []) + [k]
    return result


def configure_logging(level: Optional[Union[int, str]] = None):
    if level is None:
        level = logging.INFO
    logging.root.setLevel(level)
    handler = logging.StreamHandler(stream=sys.stderr)
    formatter = logging.Formatter("[%(asctime)s] %(levelname)s [%(name)s] %(message)s")
    handler.setFormatter(formatter)
    logging.root.addHandler(handler)


def search_files(root_folder: str,
                 glob_pattern: str,
                 include_subfolders: bool = True,
                 exclusion_patterns=None) -> List[str]:
    """
    Get a list of paths given the specified folder and pattern
    :param root_folder: root folder where to look for files
    :param glob_pattern: file name pattern
    :param include_subfolders: True to include subfolders in the search
    :param exclusion_patterns: list of patterns used to exclude matching filenames from the list
    :return: list of path names matching the given filter
    """
    if exclusion_patterns is None:
        exclusion_patterns = []
    search_pattern: str = glob_pattern
    if include_subfolders:
        search_pattern = os.path.join("**", glob_pattern)
    files_list: List[str] = glob.glob(os.path.join(root_folder, search_pattern), recursive=True)
    result = []
    for bgl_file_path in files_list:
        exclusion_match = False
        for exclusion_pattern in exclusion_patterns:
            if exclusion_pattern.lower() in bgl_file_path.lower():
                exclusion_match = True
                break
            else:
                pass
        if not exclusion_match:
            result.append(bgl_file_path)
    return result


FSX_MAIN_DIR = "C:\\Program Files (x86)\\Microsoft Games\\Microsoft Flight Simulator X"
FSX_ADDON_SCENERY_DIR = os.path.join(FSX_MAIN_DIR, "Addon Scenery")
FSX_STOCK_SCENERY_DIR = os.path.join(FSX_MAIN_DIR, "Scenery")
FSX_SIMOBJECTS_DIR = os.path.join(FSX_MAIN_DIR, "SimObjects")
FSX_TEXTURES_DIR = os.path.join(FSX_MAIN_DIR, "texture"),

FS9_MAIN_DIR = "C:\\Program Files (x86)\\Microsoft Games\\Microsoft Flight Simulator 2004"
FS9_ADDON_SCENERY_DIR = os.path.join(FS9_MAIN_DIR, "Addon Scenery")
