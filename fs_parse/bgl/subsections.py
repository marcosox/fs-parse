import struct
from typing import List, Optional, Type

from fs_parse.bgl.records.modeldata import ModelDataRecord
from fs_parse.bgl.records.sceneryobject import SCENERYOBJECTS_IDS, SceneryObjectRecord
from fs_parse.datatypes import Unpackable


class BGLSubSectionHeader(Unpackable):
    """ Generic subsection header """

    def __init__(self):
        super().__init__()
        self.QMID_a: Optional[int] = None
        self.QMID_b: Optional[int] = None
        self.records_number: Optional[int] = None
        self.first_record_file_offset: Optional[int] = None
        self.subsection_data_size: Optional[int] = None

    def parse(self, bgl_file_data: bytes, file_offset: int):
        raise NotImplementedError


class BGLStandardSubSectionHeader(BGLSubSectionHeader):
    """ The most common subsection type. Subclassed by the section-specific types """
    fmt = '@4L'

    def parse(self, bgl_file_data: bytes, file_offset: int):
        (self.QMID_a,
         self.records_number,
         self.first_record_file_offset,
         self.subsection_data_size) = self.get_data(bgl_file_data, file_offset)
        # self.QMID_b = None


class BGLTerrainSubSectionHeader(BGLSubSectionHeader):
    """ Subsection type with a larger header """
    fmt = '@5L'
    bytes_size = struct.calcsize(fmt)

    def parse(self, bgl_file_data: bytes, file_offset: int):
        (self.QMID_a,
         self.QMID_b,
         self.records_number,
         self.first_record_file_offset,
         self.subsection_data_size) = self.get_data(bgl_file_data, file_offset)


class BGLSubSection(Unpackable):
    """ Base subsection class - do not instantiate directly """
    header_type = BGLStandardSubSectionHeader

    def __init__(self):
        super().__init__()
        self.header: BGLSubSectionHeader = self.header_type()
        self.records: list = []

    def parse(self, bgl_file_data: bytes, file_offset: int):
        self.header.parse(bgl_file_data, file_offset)

    @property
    def basic_info(self) -> str:
        return f"Subsection ({self.header.subsection_data_size} bytes), {self.header.records_number} records starting at {hex(self.header.first_record_file_offset)}"

    def __str__(self):
        return f"{self.__class__.__name__} {self.basic_info}"


class ModelData(BGLSubSection):
    """ Container for library model objects """
    header_type = BGLStandardSubSectionHeader

    def __init__(self, skip_invalid: bool = True):
        super(ModelData, self).__init__()
        self.skip_invalid: bool = skip_invalid
        self.records: List[ModelDataRecord] = []

    def parse(self, bgl_file_data: bytes, file_offset: int):
        super(ModelData, self).parse(bgl_file_data, file_offset)
        for i in range(0, self.header.records_number):
            record_offset = self.header.first_record_file_offset + (i * struct.calcsize(ModelDataRecord.fmt))
            try:
                record = ModelDataRecord()
                record.parse(bgl_file_data, record_offset)
                self.records.append(record)
            except Exception as e:
                self._logger.exception(f"Couldn't deserialize record {i}")
                if self.skip_invalid:
                    continue
                else:
                    raise e


class SceneryObject(BGLSubSection):
    header_type = BGLStandardSubSectionHeader

    def __init__(self):
        super(SceneryObject, self).__init__()
        self.records: List[SceneryObjectRecord] = []

    def parse(self, bgl_file_data: bytes, file_offset: int):
        super(SceneryObject, self).parse(bgl_file_data, file_offset)
        current_record_offset: int = self.header.first_record_file_offset
        for i in range(0, self.header.records_number):
            self._logger.debug(f"record {i} @{hex(current_record_offset)}")
            # detect next record type from first 2 bytes
            (decoded_id, record_size) = struct.unpack("@2H", bgl_file_data[current_record_offset:current_record_offset + 4])
            record_class: Type[SceneryObjectRecord] = SCENERYOBJECTS_IDS.get(decoded_id, None)
            if record_class:
                try:
                    record: SceneryObjectRecord = record_class()
                    record.parse(bgl_file_data, current_record_offset)
                    self.records.append(record)
                    current_record_offset += record.total_size  # use the declared value so it advances even on still-unmanaged records
                except Exception as e:
                    self._logger.error(f"Error parsing scenery record {i} at offset {hex(current_record_offset)}")
                    raise e
            else:
                raise Exception(f"UNKNOWN scenery object type {hex(decoded_id)} for record {i} at offset {hex(current_record_offset)} with declared size {hex(record_size)}")
