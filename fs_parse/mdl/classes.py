import logging

from fs_parse.datatypes import FixedSizeStruct, UnpackableBuffer


class RIFFSectionHeader(UnpackableBuffer):
    data_format = [
        FixedSizeStruct("4sL")
    ]

    def __init__(self):
        self.type_id: str = ""
        self.data_size: int = 0

    def parse(self, mdl_file_data: bytes, file_offset: int):
        (type_id, self.data_size) = self.get_data(mdl_file_data, file_offset)
        assert isinstance(type_id, bytes)
        self.type_id = str(type_id, 'utf-8')

    def __str__(self):
        return f"[{self.type_id}]({self.data_size} bytes)"


class MDLSection(UnpackableBuffer):
    data_format = None

    def __init__(self, header: RIFFSectionHeader):
        self._logger: logging.Logger = logging.getLogger(self.__class__.__name__)
        self.header: RIFFSectionHeader = header

    def parse(self, mdl_file_data: bytes, file_offset: int):
        raise NotImplementedError

    @property
    def size(self):
        return self.header.data_size + 8

    def __str__(self):
        data = self.to_dict()
        data.pop("header", None)
        props = ", ".join([f"{k}={v}" for k, v in data.items()])
        return f"{self.header} {props}"


class PlaceHolderMDLSection(MDLSection):

    def parse(self, mdl_file_data: bytes, file_offset: int):
        pass

    def __str__(self):
        return f"[{self.header.type_id}] ({self.header.data_size} bytes)"
