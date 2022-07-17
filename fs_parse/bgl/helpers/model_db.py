import json
import logging
import os.path
from typing import Dict, List

from bgl.classes import BGLFile
from utils import FSX_ADDON_SCENERY_DIR, FSX_STOCK_SCENERY_DIR, search_files


class ModelsDB:
    def __init__(self,
                 cache_path: str = ".modelsdb.json",
                 include_stock: bool = True,
                 include_addon: bool = False,
                 force_empty_cache: bool = False):
        """
        Memory database object storing lib objects definitions and placements, indexed with their respective files
        :param cache_path: cache file to store results. Refresh if files change
        """
        self._logger: logging.Logger = logging.getLogger(self.__class__.__name__)
        self._file_2_uuids: Dict[str, List[str]] = {}
        self._uuid_2_files: Dict[str, List[str]] = {}
        self._placement_2_files: Dict[str, List[str]] = {}
        self._file_2_placements: Dict[str, List[str]] = {}
        self.cache_path: str = cache_path
        if force_empty_cache or not os.path.isfile(self.cache_path):
            self.save()
        else:
            self.load()
        if include_stock:
            self._logger.info("Populating models DB with stock objects and placements... (this could take some minutes)")
            self.scan(FSX_STOCK_SCENERY_DIR, exclusion_patterns=["\\cvx", "\\dem", "\\brx"])
        if include_addon:
            self._logger.info("Populating models DB with addon scenery objects and placements... (this could take some minutes)")
            self.scan(FSX_ADDON_SCENERY_DIR, exclusion_patterns=["\\cvx"])

    @property
    def file_2_uuids(self):
        """ Mapping File -> list of UUIDs defined in it """
        return self._file_2_uuids

    @property
    def uuid_2_files(self):
        """ Mapping UUID -> list of files with a placement for it """
        return self._uuid_2_files

    @property
    def file_2_placements(self):
        """ Mapping File -> list of UUIDs placed by it """
        return self._file_2_placements

    @property
    def placement_2_files(self):
        """ Mapping UUID -> list of files defining it """
        return self._placement_2_files

    @property
    def files(self):
        return self._file_2_uuids.keys()

    @property
    def uuids(self):
        return self._uuid_2_files.keys()

    @property
    def has_cache(self) -> bool:
        return os.path.isfile(self.cache_path)

    def scan(self,
             path: str,
             exclusion_patterns=None,
             force_scan=False):
        """
        Scan a path for bgl files and index their object definitions

        :param path: folder or single file to scan. Scan is recursive.
        :param exclusion_patterns: list of substrings used to match and exclude files from the final result
        :param force_scan: if False and at least one valid file from the path is already in the cache,
         the scan is not performed and the cache version is assumed to be up to date.
        :return: None
        """
        if (not force_scan) and any([p.startswith(path) for p in self.files]):
            return
        if exclusion_patterns is None:
            exclusion_patterns = []
        bgl_files_list = search_files(root_folder=path,
                                      glob_pattern="*.bgl",
                                      exclusion_patterns=exclusion_patterns)
        total_files_count = len(bgl_files_list)
        self._logger.debug(f"Found {total_files_count} bgl files")
        for i, bgl_file_path in enumerate(bgl_files_list, start=1):
            self._logger.info(f"Scanning [{i}/{total_files_count}] {bgl_file_path}")
            bgl_file = BGLFile.from_file(bgl_file_path)
            object_guids = [str(record.uuid) for record in bgl_file.get_models()]
            if object_guids:
                self._file_2_uuids[bgl_file_path] = [x for x in object_guids]
                for guid in object_guids:
                    self._uuid_2_files[guid] = self._uuid_2_files.get(guid, []) + [bgl_file_path]
            placement_guids = [str(record.obj_info.name) for record in bgl_file.get_placements()]
            if placement_guids:
                self._file_2_placements[bgl_file_path] = list(set([x for x in placement_guids]))
                for guid in placement_guids:
                    self._placement_2_files[guid] = list(set(self._placement_2_files.get(guid, []) + [bgl_file_path]))
        self._logger.info(f"Found {len(self._uuid_2_files.keys())} definitions in {len(self._file_2_uuids.keys())} files")
        self._logger.info(f"Found {len(self._placement_2_files.keys())} placements in {len(self._file_2_placements.keys())} files")
        self.save()

    def save(self):
        """ Persists the DB to the file specified by self.cache_path """
        with open(self.cache_path, "w") as outfile:
            outfile.write(json.dumps(
                {
                    "file_2_uuids": self.file_2_uuids,
                    "uuid_2_files": self.uuid_2_files,
                    "placement_2_files": self.placement_2_files,
                    "file_2_placements": self.file_2_placements,
                },
                indent=2,
                sort_keys=True))

    def load(self, path: str = None):
        """ Load the DB from the given file or the one specified in self.cache_path """
        path = path or self.cache_path
        with open(path, "r") as infile:
            file_contents = json.loads(infile.read())
        for field in ["file_2_uuids", "uuid_2_files", "placement_2_files", ]:
            if field not in file_contents:
                raise Exception(f"Missing '{field}' in {path} while trying to load models DB")
        self._file_2_uuids = file_contents['file_2_uuids']
        self._uuid_2_files = file_contents['uuid_2_files']
        self._placement_2_files = file_contents['placement_2_files']
        self._file_2_placements = file_contents['_file_2_placements']

    def clear(self):
        """ Empty the DB """
        self._file_2_uuids = {}
        self._uuid_2_files = {}
        self._placement_2_files = {}
        self._file_2_placements = {}
