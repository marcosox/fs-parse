import logging
import struct
from typing import Any, List, Optional, Tuple

from fs_parse.utils import bytes_2_hexstr, read_stringz, read_stringz_word_aligned


class Unpackable:
    fmt: Optional[str] = None

    def __init__(self):
        self._logger: logging.Logger = logging.getLogger(self.__class__.__name__)
        self.offset: int = 0
        self.raw_data: bytes = bytes()

    @property
    def fmt_bytes_size(self):
        return struct.calcsize(self.fmt)

    def get_data(self, buffer: bytes, offset: int) -> tuple:
        self.offset = offset
        self.raw_data = buffer[offset:offset + self.fmt_bytes_size]
        result = struct.unpack(self.fmt, self.raw_data)
        self._logger.debug(f"@{hex(self.offset)}: {bytes_2_hexstr(self.raw_data)} -> {result}")
        return result

    def parse(self, bgl_file_data: bytes, file_offset: int):
        raise NotImplementedError


class DataValue:

    @property
    def size(self) -> int:
        raise NotImplementedError

    def parse(self, buffer, offset) -> Tuple[Any, ...]:
        raise NotImplementedError


class FixedSizeStruct(DataValue):
    def __init__(self, format_string: str = ""):
        self.format_string: str = format_string

    @property
    def size(self) -> int:
        return struct.calcsize(self.format_string)

    def parse(self, buffer, offset) -> Tuple[Any, ...]:
        return struct.unpack(self.format_string, buffer[offset:offset + self.size])


class StringZ(DataValue):

    def __init__(self):
        self._data: str = ""

    @property
    def size(self) -> int:
        if self._data:
            return len(self._data) + 1
        else:
            raise Exception(f"You must call .parse() on this {self.__class__.__name__} object before accessing its size")

    def parse(self, buffer, offset) -> Tuple[Any, ...]:
        self._data = read_stringz(buffer[offset:])
        return self.size, self._data


class WordAlignedStringZ(DataValue):

    def __init__(self):
        self._raw_size: Optional[int] = None

    @property
    def size(self) -> int:
        if self._raw_size is not None:
            return self._raw_size
        else:
            raise Exception(f"You must call .parse() on this {self.__class__.__name__} object before accessing its size")

    def parse(self, buffer, offset) -> Tuple[Any, ...]:
        self._raw_size, result = read_stringz_word_aligned(buffer[offset:])
        return tuple(result)


class UnpackableBuffer:
    data_format: List[DataValue] = []

    def get_data(self, buffer: bytes, offset: int) -> tuple:
        current_offset = offset
        result = []
        for dv in self.data_format:
            result.extend(dv.parse(buffer, current_offset))
            current_offset += dv.size
        return tuple(result)

    def to_dict(self) -> dict:
        return {
            k: v for k, v in
            vars(self).copy().items()
            if not k.startswith("_")
        }

    def parse(self, mdl_file_data: bytes, file_offset: int):
        raise NotImplementedError

    @property
    def size(self):
        return sum([df.size for df in self.data_format])
