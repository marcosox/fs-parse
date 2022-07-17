"""
Analyze a simobject folder (e.g. an airplane) and list all textures for the models declared in aircraft.cfg.
Additionally, try to find each texture file and report the missing ones
"""

import logging
import os
import sys
from typing import Dict, List, Optional

from fs_parse.cfg.classes import SimObject
from fs_parse.cfg.utils import get_cfg_file_as_dict
from fs_parse.mdl.main_classes import MDLFile, UnsupportedMDLVersionException
from fs_parse.utils import FSX_SIMOBJECTS_DIR, configure_logging

LOG_FOUND_TEXTURE_FOLDER = False  # True to print where each texture file was actually found
logger = logging.getLogger(__name__)


def find_texture(texture_filename: str, textures_dirs: List[str]) -> Optional[str]:
    """
    Search for the specified texture in the correct textures folder for the given fltsim object
    :param textures_dirs: list of folders where to look in
    :param texture_filename: texture name from mdl file
    :return: the found texture path or None if the texture was not found
    """
    for folder in textures_dirs:
        candidate = os.path.join(folder, texture_filename)
        if os.path.exists(candidate):
            return candidate
        else:
            # check with a different extension
            texture_name_no_ext, _ = os.path.splitext(candidate)
            for ext in ["dds", "bmp"]:
                candidate = f"{texture_name_no_ext}.{ext}"
                if os.path.exists(candidate):
                    return candidate


def get_mdl_texture_dicts(simobject: SimObject) -> Dict[str, Dict[str, List[str]]]:
    # preload texture names
    # get list of actual model dirs (the ones starting with "model." plus the default "model" folder)
    model_dirs = list(set([
        model_dict["model"]
        for _, model_dict in simobject.models.items()
    ]))

    logger.debug(f"found {len(model_dirs)} distinct model file folders")
    # collect mdl filenames -> texture names
    mdl_textures: Dict[str:List[str]] = {}
    for model_dir in model_dirs:
        mdl_textures[model_dir] = {}
        try:
            model_cfg = get_cfg_file_as_dict(os.path.join(model_dir, "model.cfg"))
        except FileNotFoundError:
            logger.warning(f"model.cfg not found in {model_dir}, skipping")
            continue
        interior_mdl = model_cfg.get("models", {}).get("interior", None)
        exterior_mdl = model_cfg.get("models", {}).get("normal", None)
        crash_mdl = model_cfg.get("models", {}).get("crash", None)
        mdl_file_paths = [
            os.path.join(model_dir, p)
            for p in [
                exterior_mdl, interior_mdl, crash_mdl
            ]
            if p
        ]
        logger.debug(f"Parsed {len(mdl_file_paths)} model files in {model_dir}")
        for file_path in mdl_file_paths:
            if not file_path.lower().endswith(".mdl"):
                file_path = f"{file_path}.mdl"
            try:
                mdlfile = MDLFile.from_file(file_path, metadata_only=True)
            except UnsupportedMDLVersionException as e:
                logger.warning(f"Skipping unsupported MDL version '{e.args[0]}' for {file_path}")
                continue
            textures = mdlfile.get_texture_names()
            if not textures:
                logger.warning("no texture section found (is this a FS9 file?)")
            logger.debug(f"Read {len(textures)} texture names from {file_path}")
            mdl_textures[model_dir][file_path] = textures
    return mdl_textures


def list_textures(simobject_folder: str):
    try:
        simobject = SimObject(simobject_folder)
    except FileNotFoundError:
        logger.info(f"Skipping folder with no aircraft.cfg: {simobject_folder}")
        return
    not_found = set()
    mdl_textures = get_mdl_texture_dicts(simobject)
    for model_index, model_dict in simobject.models.items():
        mdl_files = mdl_textures[model_dict["model"]]
        for mdl_file_path, textures_list in mdl_files.items():
            relative_path = mdl_file_path.replace(f"{simobject.base_folder}{os.sep}", "")
            if not textures_list:
                logger.info(f"No textures for {relative_path}")
                continue
            for texture in textures_list:
                if texture.startswith("$"):
                    continue  # skip VC internal textures
                match_dir = find_texture(texture, simobject.get_textures_dirs_for_model(model_index))
                if not match_dir:
                    logger.debug(f"Texture {texture} for file {relative_path} in fltsim index '{model_index}' not found")
                    not_found.add((
                        relative_path,
                        f"fltsim.{model_index}",
                        texture
                    ))
                elif LOG_FOUND_TEXTURE_FOLDER:
                    logger.debug(f"\t{texture} found in {match_dir.replace(simobject.base_folder, '')}")

    # if not not_found:
    #     print(f"All textures were found for {simobject_folder.replace(FSX_SIMOBJECTS_DIR, '')}")
    # else:
    if not_found:
        print(f"{len(not_found)} textures were not found for {simobject_folder.replace(FSX_SIMOBJECTS_DIR, '')}:")
        for t in not_found:
            print(f"\t{t}")


def main():
    configure_logging(level=logging.WARNING)
    if len(sys.argv) <= 1:
        logger.info("No argument specified, scanning the entire Airplanes section")
        base_dir = os.path.join(FSX_SIMOBJECTS_DIR, "Airplanes")
        search_folders = [os.path.join(base_dir, d) for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
    else:
        search_folders = [os.path.join(FSX_SIMOBJECTS_DIR, sys.argv[1])]
    for folder in search_folders:
        list_textures(folder)


if __name__ == '__main__':
    main()
