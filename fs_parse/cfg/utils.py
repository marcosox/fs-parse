import configparser
import os
import re

from typing import List


def get_cfg_file_as_dict(file_path: str) -> dict:
    """ Parse a .cfg file as a dict """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(file_path)
    aircraft_config = configparser.ConfigParser(comment_prefixes=[";", "#", "//", "--"],
                                                inline_comment_prefixes=["//"],
                                                strict=False,
                                                interpolation=None)
    aircraft_config.read(file_path)
    result = {
        section: dict(aircraft_config[section])
        for section in aircraft_config.sections()
    }
    return result


def get_simobject_fallback_textures_folders(texture_cfg_path: str) -> List[str]:
    """
    Get the list of the textures fallback folders from a texture.cfg file
    :param texture_cfg_path: texture.cfg file path
    :return: list of absolute paths of texture folders for this texture.cfg's model
    """
    if not texture_cfg_path.lower().endswith(f"{os.sep}texture.cfg"):
        file_dir = texture_cfg_path
        texture_cfg_path = os.path.join(file_dir, "texture.cfg")
    else:
        file_dir, _ = os.path.split(texture_cfg_path)
    try:
        texture_config = get_cfg_file_as_dict(texture_cfg_path)
    except FileNotFoundError:
        texture_config = {}
    result = []
    for k, v in texture_config.get("fltsim", {}).items():
        if re.match("fallback\\.\\d+", k) is not None:
            result.append(os.path.abspath(os.path.join(file_dir, v)))
    return result
