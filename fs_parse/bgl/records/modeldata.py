import uuid

from fs_parse.datatypes import Unpackable


class ModelDataRecord(Unpackable):
    """ Library object model. Encapsulates an MDL file """

    fmt = '@16s2L'

    def __init__(self):
        super().__init__()
        self.mdl_file_offset: int = 0
        self.mdl_file_length: int = 0
        self.uuid: uuid.UUID = uuid.UUID(int=0)
        self.mdl_data: bytes = bytes()

    def parse(self, bgl_file_data: bytes, file_offset: int):
        fields = self.get_data(bgl_file_data, file_offset)
        (uuid_value,
         self.mdl_file_offset,
         self.mdl_file_length) = fields
        self.uuid = uuid.UUID(bytes_le=uuid_value)
        self.mdl_data: bytes = bgl_file_data[self.mdl_file_offset:self.mdl_file_offset + self.mdl_file_length]

    def __str__(self):
        return f"{self.__class__.__name__} {self.uuid} ({self.mdl_file_length} bytes starting at {hex(self.mdl_file_offset)})"
