"""
Classes representing BGL files and their contents
"""
import datetime
import logging
import struct
from typing import List, Optional

from fs_parse.bgl.constants import BGLSectionType
from fs_parse.bgl.records.modeldata import ModelDataRecord
from fs_parse.bgl.records.sceneryobject import LibraryObjectRecord
from fs_parse.bgl.subsections import BGLSubSection, ModelData, SceneryObject
from fs_parse.datatypes import Unpackable


class BGLHeader(Unpackable):
    fmt = '@2LQ10L'

    def __init__(self, file_path: Optional[str] = None):
        super().__init__()
        self.file_path: Optional[str] = file_path
        self.magic_number_1: int = 0x19920201
        self.header_size: int = 0
        self.filetime: datetime.datetime = datetime.datetime.now()
        self.magic_number_2: int = 0x08051803
        self.sections_count: int = 0
        self.qmid_slots: List[int] = []

    def parse(self, bgl_file_data: bytes, file_offset: int = 0):
        (self.magic_number_1,
         self.header_size,
         filetime_100_ns_intervals,
         self.magic_number_2,
         self.sections_count,
         *self.qmid_slots) = self.get_data(bgl_file_data, file_offset)
        base_datetime = datetime.datetime(year=1601, month=1, day=1, hour=0, minute=0, second=0)
        microseconds = int(filetime_100_ns_intervals / 10)
        try:
            self.filetime: datetime.datetime = base_datetime + datetime.timedelta(microseconds=microseconds)
        except OverflowError:
            # if the filetime value is wrong, it's encoded as a nanoseconds epoch timestamp
            base_datetime_epoch = datetime.datetime(year=1970, month=1, day=1, hour=0, minute=0, second=0)
            nanoseconds = int(microseconds / 1000)
            self.filetime: datetime.datetime = base_datetime_epoch + datetime.timedelta(microseconds=nanoseconds)


class BGLSection(Unpackable):
    subsections_mapping = {
        BGLSectionType.NONE: None,
        BGLSectionType.COPYRIGHT: None,
        BGLSectionType.GUID: BGLSubSection,
        BGLSectionType.AIRPORT: BGLSubSection,
        BGLSectionType.ILS_VOR: BGLSubSection,
        BGLSectionType.NDB: BGLSubSection,
        BGLSectionType.MARKER: BGLSubSection,
        BGLSectionType.BOUNDARY: BGLSubSection,
        BGLSectionType.WAYPOINT: BGLSubSection,
        BGLSectionType.GEOPOL: BGLSubSection,
        BGLSectionType.SCENERYOBJECT: SceneryObject,
        BGLSectionType.NAMELIST: BGLSubSection,
        BGLSectionType.VORILSICAOINDEX: BGLSubSection,
        BGLSectionType.NDBICAOINDEX: BGLSubSection,
        BGLSectionType.WAYPOINTICAOINDEX: BGLSubSection,
        BGLSectionType.MODELDATA: ModelData,
        BGLSectionType.AIRPORTSUMMARY: BGLSubSection,
        BGLSectionType.EXCLUSION: BGLSubSection,
        BGLSectionType.TIMEZONE: BGLSubSection,
        BGLSectionType.TERRAINVECTORDB: BGLSubSection,
        BGLSectionType.TERRAINELEVATION: BGLSubSection,
        BGLSectionType.TERRAINLANDCLASS: BGLSubSection,
        BGLSectionType.TERRAINWATERCLASS: BGLSubSection,
        BGLSectionType.TERRAINREGION: BGLSubSection,
        BGLSectionType.POPULATIONDENSITY: BGLSubSection,
        BGLSectionType.AUTOGENANNOTATION: BGLSubSection,
        BGLSectionType.TERRAININDEX: BGLSubSection,
        BGLSectionType.TERRAINTEXTURELOOKUP: BGLSubSection,
        BGLSectionType.TERRAINSEASONJAN: BGLSubSection,
        BGLSectionType.TERRAINSEASONFEB: BGLSubSection,
        BGLSectionType.TERRAINSEASONMAR: BGLSubSection,
        BGLSectionType.TERRAINSEASONAPR: BGLSubSection,
        BGLSectionType.TERRAINSEASONMAY: BGLSubSection,
        BGLSectionType.TERRAINSEASONJUN: BGLSubSection,
        BGLSectionType.TERRAINSEASONJUL: BGLSubSection,
        BGLSectionType.TERRAINSEASONAUG: BGLSubSection,
        BGLSectionType.TERRAINSEASONSEP: BGLSubSection,
        BGLSectionType.TERRAINSEASONOCT: BGLSubSection,
        BGLSectionType.TERRAINSEASONNOV: BGLSubSection,
        BGLSectionType.TERRAINSEASONDEC: BGLSubSection,
        BGLSectionType.TERRAINPHOTOJAN: BGLSubSection,
        BGLSectionType.TERRAINPHOTOFEB: BGLSubSection,
        BGLSectionType.TERRAINPHOTOMAR: BGLSubSection,
        BGLSectionType.TERRAINPHOTOAPR: BGLSubSection,
        BGLSectionType.TERRAINPHOTOMAY: BGLSubSection,
        BGLSectionType.TERRAINPHOTOJUN: BGLSubSection,
        BGLSectionType.TERRAINPHOTOJUL: BGLSubSection,
        BGLSectionType.TERRAINPHOTOAUG: BGLSubSection,
        BGLSectionType.TERRAINPHOTOSEP: BGLSubSection,
        BGLSectionType.TERRAINPHOTOOCT: BGLSubSection,
        BGLSectionType.TERRAINPHOTONOV: BGLSubSection,
        BGLSectionType.TERRAINPHOTODEC: BGLSubSection,
        BGLSectionType.TERRAINPHOTONIGHT: BGLSubSection,
        BGLSectionType.TACAN: BGLSubSection,
        BGLSectionType.TACANINDEX: BGLSubSection,
        BGLSectionType.FAKETYPES: BGLSubSection,
        BGLSectionType.ICAORUNWAY: BGLSubSection,
    }
    fmt = '@5L'

    def __init__(self):
        super().__init__()
        self.section_type: BGLSectionType = BGLSectionType.NONE
        self.subsection_size_value: int = 0
        self.subsections_count: int = 0
        self.sections_start_offset: int = 0
        self.total_size: int = 0
        self.subsections: List[BGLSubSection] = []

    def parse(self, bgl_file_data: bytes, file_offset: int):
        fields = self.get_data(bgl_file_data, file_offset)
        (self.section_type,
         self.subsection_size_value,
         self.subsections_count,
         self.sections_start_offset,
         self.total_size) = fields
        self.section_type: BGLSectionType = BGLSectionType(self.section_type)
        self.subsection_size_value: int = ((self.subsection_size_value & 0x10000) | 0x40000) >> 0x0E
        subsection_class = self.subsections_mapping[self.section_type]
        for i in range(0, self.subsections_count):
            subsection_offset = self.sections_start_offset + (i * self.subsection_size_value)
            subsection = subsection_class()
            subsection.parse(bgl_file_data, subsection_offset)
            self.subsections.append(subsection)

    def __str__(self):
        return f"{hex(self.section_type.value)} {self.section_type.name} section, {self.subsections_count} subsections ({self.subsection_size_value} bytes each) starting at {hex(self.sections_start_offset)}"


class BGLFile:
    def __init__(self, file_path: Optional[str] = None):
        self._logger = logging.getLogger(self.__class__.__name__)
        self.header: BGLHeader = BGLHeader(file_path=file_path)
        self.sections: List[BGLSection] = []

    def parse(self, bgl_file_data: bytes):
        self.header.parse(bgl_file_data)
        for i in range(0, self.header.sections_count):
            # sections start right after the header
            self._logger.debug(f"\tSection {i}")
            section_offset = self.header.fmt_bytes_size + (i * struct.calcsize(BGLSection.fmt))
            section = BGLSection()
            section.parse(bgl_file_data, section_offset)
            self._logger.debug(f"\t {hex(section.section_type)} - {BGLSectionType(section.section_type).name}")
            self.sections.append(section)

    def get_placements(self) -> List[LibraryObjectRecord]:
        """ Return a list of LibraryObject records (library object placements) """
        result = []
        for section in self.sections:
            if section.section_type == BGLSectionType.SCENERYOBJECT:
                for subsection in section.subsections:
                    result.extend([record for record in subsection.records if isinstance(record, LibraryObjectRecord)])
        return result

    def get_models(self) -> List[ModelDataRecord]:
        """ Return a list of ModelData records (library object models) """
        result = []
        for section in self.sections:
            if section.section_type == BGLSectionType.MODELDATA:
                for subsection in section.subsections:
                    assert isinstance(subsection, ModelData)
                    subsection: ModelData
                    result.extend(subsection.records)
        return result

    @classmethod
    def from_file(cls, file_path: str):
        """ Create a new BGLFile object from a file path """
        with open(file_path, "rb") as infile:
            file_bytes: bytes = infile.read()
        result = cls(file_path=file_path)
        result.parse(file_bytes)
        return result

    def __str__(self):
        return f"BGL file ({self.header.sections_count} sections)"
