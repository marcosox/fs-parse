import logging
import os.path
from typing import Any, Dict, List

from fs_parse.cfg.utils import get_cfg_file_as_dict, get_simobject_fallback_textures_folders


class SimObject:
    def __init__(self, base_folder: str):
        if not os.path.exists(base_folder):
            raise FileNotFoundError(base_folder)
        self.logger: logging.Logger = logging.getLogger(self.__class__.__name__)
        self.base_folder: str = base_folder
        self.object_type_folder: str = os.path.dirname(self.base_folder)
        self.aircraft_cfg_file_path: str = os.path.join(self.base_folder, "aircraft.cfg")
        self.aircraft_cfg: dict = get_cfg_file_as_dict(self.aircraft_cfg_file_path)

    def _get_alias_folder(self, file_cfg_path: str):
        """ Return the alias folder defined in this cfg file, or None if not defined """
        model_dir, _ = os.path.split(file_cfg_path)
        file_dict = get_cfg_file_as_dict(file_cfg_path)
        if file_dict.get("fltsim", {}).get("alias", None):
            alias_dir = file_dict["fltsim"]["alias"]
            if os.path.isabs(alias_dir):
                # alias from absolute path
                result = os.path.abspath(os.path.join(self.object_type_folder, alias_dir[1:]))
            else:
                # alias from relative path
                result = os.path.abspath(os.path.join(model_dir, alias_dir))
        else:
            result = None
        return result

    def _resolve_model_folder(self, model_section_entry: str) -> str:
        """
        Get the absolute path of the model folder declared in the aircraft.cfg file.
        If there is an alias declared, it is resolved and returned.
        So the actual model folder could be outside of self.base_dir
        :param model_section_entry: "model" option value from the aircraft.cfg file
        :return: absolute path of the model folder for this variation
        """
        if not model_section_entry:
            model_section_entry = "model"
        else:
            model_section_entry = f"model.{model_section_entry}"
        model_abs_dir = os.path.abspath(os.path.join(self.base_folder, model_section_entry))
        try:
            alias_dir = self._get_alias_folder(os.path.join(model_abs_dir, "model.cfg"))
        except FileNotFoundError:
            alias_dir = None
        while alias_dir is not None:
            model_abs_dir = alias_dir
            alias_dir = self._get_alias_folder(os.path.join(model_abs_dir, "model.cfg"))
        return model_abs_dir

    def _resolve_texture_folder(self, texture_section_entry: str) -> str:
        """
        Get the absolute path of the texture folder declared in the aircraft.cfg file
        :param texture_section_entry: "texture" option value from the aircraft.cfg file
        :return: absolute path of the texture folder for this variation
        """
        if not texture_section_entry:
            texture_section_entry = "texture"
        else:
            texture_section_entry = f"texture.{texture_section_entry}"
        return os.path.abspath(os.path.join(self.base_folder, texture_section_entry))

    @property
    def models(self) -> Dict[str, Dict[str, Any]]:
        """
        Dictionary of fltsim sections from the aircraft.cfg file, with resolved paths for model and texture section.
        Root keys are the suffixes of fltsim.NNNN sections

            {
                "001":{
                    "model": "C:\\Program files...",
                    "texture": "C:\\Pro...",
                    ...
                },
                "002": {
                    ...
                },
                ...
            }

        :return: fltsim sections dictionary
        """
        result = {}
        for k, v in self.aircraft_cfg.items():
            if k.startswith("fltsim."):
                entry = dict(v)
                entry['model'] = self._resolve_model_folder(entry.get("model", ""))
                entry['texture'] = self._resolve_texture_folder(entry.get("texture", ""))
                result[k.replace("fltsim.", "")] = entry
        return result

    def get_textures_dirs_for_model(self, fltsim_index: str) -> List[str]:
        """ Return the list of folders where the given model will look for textures """
        variation_textures_dir = self.models[fltsim_index]["texture"]
        fallback_textures_dirs = get_simobject_fallback_textures_folders(os.path.join(variation_textures_dir, "texture.cfg"))
        return list({variation_textures_dir, *fallback_textures_dirs})
