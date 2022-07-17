import struct
import uuid
from typing import List

from fs_parse.datatypes import DataValue, FixedSizeStruct, StringZ
from fs_parse.mdl.classes import MDLSection, RIFFSectionHeader


class MDLHSection(MDLSection):
    """
    This the FS MDL object header.
    """
    data_format: List[DataValue] = [
        FixedSizeStruct("Lf"),
    ]

    def __init__(self, header: RIFFSectionHeader):
        super().__init__(header)
        self.magic_number: int = 123456
        self.model_version: float = 10.0

    def parse(self, mdl_file_data: bytes, file_offset: int):
        (self.magic_number, self.model_version) = self.get_data(mdl_file_data, file_offset)


class MDLGSection(MDLSection):
    """
    This section stores the object GUID.
    """
    data_format: List[DataValue] = [
        FixedSizeStruct("16s"),
    ]

    def __init__(self, header: RIFFSectionHeader):
        super().__init__(header)
        self.uuid: uuid.UUID = uuid.UUID(int=0)

    def parse(self, mdl_file_data: bytes, file_offset: int):
        (guid,) = self.get_data(mdl_file_data, file_offset)
        self.uuid = uuid.UUID(bytes_le=guid)


class MDLNSection(MDLSection):
    """
    This section contains a string with the friendly name of the object.
    """
    data_format: List[DataValue] = [
        StringZ()
    ]

    def __init__(self, header: RIFFSectionHeader):
        super().__init__(header)
        self.name: str = ""

    def parse(self, mdl_file_data: bytes, file_offset: int):
        (name_len, self.name) = self.get_data(mdl_file_data, file_offset)


class SMAPSection(MDLSection):
    """
    Unknown
    """

    def __init__(self, header: RIFFSectionHeader):
        super().__init__(header)
        self.raw_data: bytes = b''

    def parse(self, mdl_file_data: bytes, file_offset: int):
        self.raw_data = mdl_file_data[file_offset:file_offset + self.header.data_size]


class PARASection(MDLSection):
    """
    This is the ParamsBlock section, containing parameter block data.
    """

    def __init__(self, header: RIFFSectionHeader):
        super().__init__(header)
        self.params_block_data: bytes = b''

    def parse(self, mdl_file_data: bytes, file_offset: int):
        self.params_block_data = mdl_file_data[file_offset:file_offset + self.header.data_size]


class CRASSection(MDLSection):
    """
    This section stores the crashtree of the object.
    """
    data_format = [
        FixedSizeStruct("2L6fL")
    ]

    def __init__(self, header: RIFFSectionHeader):
        super().__init__(header)
        self.unknown_1: int = 0
        self.unknown_2: int = 0
        self.minx: float = 0.0  # starting point is in the front lower left corner
        self.miny: float = 0.0
        self.minz: float = 0.0
        self.length: float = 0.0
        self.height: float = 0.0
        self.width: float = 0.0
        self.nodes_count: int = 0
        self.cells: List[int] = []

    def parse(self, mdl_file_data: bytes, file_offset: int):
        (self.unknown_1,
         self.unknown_2,
         self.minx,
         self.miny,
         self.minz,
         self.length,
         self.height,
         self.width,
         self.nodes_count,) = self.get_data(mdl_file_data, file_offset)
        current_offset = file_offset + sum([dv.size for dv in self.data_format])
        cell_format = "l"
        for i in range(0, self.nodes_count):
            cell_offset = current_offset + (i * 4)
            (cell_value,) = struct.unpack(cell_format, mdl_file_data[cell_offset:cell_offset + 4])
            self.cells.append(cell_value)


class BBOXSection(MDLSection):
    """
    This section stores the bounding box of the object.
    """
    data_format: List[DataValue] = [
        FixedSizeStruct("6f")
    ]

    def __init__(self, header: RIFFSectionHeader):
        super().__init__(header)
        self.xmin: float = 0.0
        self.ymin: float = 0.0
        self.zmin: float = 0.0
        self.xmax: float = 0.0
        self.ymax: float = 0.0
        self.zmax: float = 0.0

    def parse(self, mdl_file_data: bytes, file_offset: int):
        (self.xmin,
         self.ymin,
         self.zmin,
         self.xmax,
         self.ymax,
         self.zmax,) = self.get_data(mdl_file_data, file_offset)


class RADISection(MDLSection):
    """
    This section stores the radius of the object.
    """
    data_format: List[DataValue] = [
        FixedSizeStruct("f")
    ]

    def __init__(self, header: RIFFSectionHeader):
        super().__init__(header)
        self.radius: float = 0.0

    def parse(self, mdl_file_data: bytes, file_offset: int):
        (self.radius,) = self.get_data(mdl_file_data, file_offset)
