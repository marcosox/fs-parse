import logging
from typing import Dict, List, Optional

from fs_parse.datatypes import DataValue, FixedSizeStruct, UnpackableBuffer
from fs_parse.mdl.classes import MDLSection, RIFFSectionHeader
from fs_parse.mdl.header_classes import BBOXSection, CRASSection, MDLGSection, MDLHSection, MDLNSection, PARASection, RADISection, SMAPSection
from fs_parse.mdl.mdld_classes import MDLDSection


class UnsupportedMDLVersionException(BaseException):
    pass


class RIFFSection(MDLSection):
    """
    The main RIFF section, comprising the entire file
    """
    data_format: List[DataValue] = [
        FixedSizeStruct("4s"),
    ]

    section_types: Dict[str, type(MDLSection)] = {
        "MDLH": MDLHSection,
        "MDLG": MDLGSection,
        "MDLN": MDLNSection,
        "SMAP": SMAPSection,
        "PARA": PARASection,
        "CRAS": CRASSection,
        "BBOX": BBOXSection,
        "RADI": RADISection,
    }

    def __init__(self, header: RIFFSectionHeader, metadata_only: bool = False):
        super().__init__(header)
        self.metadata_only: bool = metadata_only
        self.version_string: str = "MDLX"
        self.mdlh: Optional[MDLHSection] = None
        self.mdlg: Optional[MDLGSection] = None
        self.mdln: Optional[MDLNSection] = None
        self.smap: Optional[SMAPSection] = None
        self.para: Optional[PARASection] = None
        self.cras: Optional[CRASSection] = None
        self.bbox: Optional[BBOXSection] = None
        self.radi: Optional[RADISection] = None
        self.mdld: Optional[MDLDSection] = None

    def parse(self, mdl_file_data: bytes, file_offset: int):
        current_offset = file_offset
        (version_string,) = self.get_data(mdl_file_data, file_offset)
        self.version_string = str(version_string, "utf-8")
        if self.version_string != "MDLX":
            raise UnsupportedMDLVersionException(self.version_string)
        current_offset += 4
        while current_offset < (file_offset + self.header.data_size):
            header = RIFFSectionHeader()
            header.parse(mdl_file_data, current_offset)
            current_offset += 8
            section_name = header.type_id.lower()
            if header.type_id in self.section_types:
                section = self.section_types[header.type_id](header)
                section.parse(mdl_file_data, current_offset)
                if isinstance(getattr(self, section_name), list):
                    getattr(self, section_name).append(section)
                else:
                    setattr(self, section_name, section)
            elif header.type_id == "MDLD":
                section = MDLDSection(header, metadata_only=self.metadata_only)
                section.parse(mdl_file_data, current_offset)
                self.mdld = section
            else:
                raise Exception(f"Unknown section {header.type_id} at offset {current_offset}")
            current_offset += header.data_size


class MDLFile:
    """
    An MDL file instance
    """

    def __init__(self, file_path: Optional[str] = None, metadata_only: bool = False):
        self.logger: logging.Logger = logging.getLogger(self.__class__.__name__)
        self.sections: List[UnpackableBuffer] = []
        self.file_path: Optional[str] = file_path
        self.metadata_only: bool = metadata_only
        self.riff_section: RIFFSection = RIFFSection(RIFFSectionHeader(), metadata_only=metadata_only)

    def parse(self, mdl_file_data: bytes):
        self.riff_section.header.parse(mdl_file_data, 0)
        self.riff_section.parse(mdl_file_data, self.riff_section.header.size)

    def get_texture_names(self):
        result: List[str] = []
        if self.riff_section \
                and self.riff_section.mdld \
                and self.riff_section.mdld.text:
            result = self.riff_section.mdld.text.texture_names
        return result

    @classmethod
    def from_file(cls, file_path: str, metadata_only: bool = False):
        """ Create a new MDLFile object from a file path """
        with open(file_path, "rb") as infile:
            file_bytes: bytes = infile.read()
        result = cls(file_path=file_path, metadata_only=metadata_only)
        result.parse(file_bytes)
        return result

    def __str__(self):
        return f"MDL file {self.file_path if self.file_path else ''}"
