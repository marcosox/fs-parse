import math
import struct
import uuid
from enum import IntEnum
from typing import Dict, List, Optional, Tuple, Type, Union

from fs_parse.bgl.constants import BeaconType, EARTH_EQUATORIAL_CIRCUMFERENCE_M, EARTH_POLAR_CIRCUMFERENCE_M, ImageComplexity, TaxiwaySignJustification
from fs_parse.datatypes import Unpackable
from fs_parse.utils import parse_flags, parse_latitude, parse_longitude, parse_pbh_value, read_stringz, read_stringz_word_aligned


class SceneryObjectHeader(Unpackable):
    fmt = '@2H2Ll6H'

    def __init__(self):
        super(SceneryObjectHeader, self).__init__()
        self.id: int = 0
        self.size: int = 0
        self.lon_raw_value: int = 0
        self.lon: float = 0.0
        self.lat: float = 0.0
        self.lat_raw_value: int = 0
        self.alt: int = 0
        self.is_above_agl: int = 0
        self.no_autogen_suppression: bool = False
        self.no_crash: bool = False
        self.no_fog: bool = False
        self.no_shadow: bool = False
        self.no_z_write: bool = False
        self.no_z_test: bool = False
        self.pitch: float = 0.0
        self.bank: float = 0.0
        self.hdg: float = 0.0
        self.image_complexity: ImageComplexity = ImageComplexity.VERY_SPARSE
        self.unknown: int = 0

    def parse(self, bgl_file_data: bytes, file_offset: int):
        (self.id,
         self.size,
         self.lon_raw_value,
         self.lat_raw_value,
         alt,
         flags,
         pitch,
         bank,
         hdg,
         image_complexity,
         self.unknown,) = self.get_data(bgl_file_data, file_offset)
        self.lon = parse_longitude(self.lon_raw_value)
        self.lat = parse_latitude(self.lat_raw_value)
        self.alt = alt / 1000.0
        (self.is_above_agl,
         self.no_autogen_suppression,
         self.no_crash,
         self.no_fog,
         self.no_shadow,
         self.no_z_write,
         self.no_z_test) = parse_flags(flags)
        self.pitch = parse_pbh_value(pitch)  # probably always 0
        self.bank = parse_pbh_value(bank)  # probably always 0
        self.hdg = parse_pbh_value(hdg)  # probably always 0, set in the item
        self.image_complexity = ImageComplexity(image_complexity)

    @property
    def total_size(self) -> int:
        return self.fmt_bytes_size


class FS9SceneryObjectHeader(SceneryObjectHeader):

    def __str__(self):
        return f"[FS9 SceneryObject Header] {self.__class__.__name__}"


class FSXSceneryObjectHeader(SceneryObjectHeader):
    extra_fmt = "@16s"

    def __init__(self):
        super(FSXSceneryObjectHeader, self).__init__()
        self.instance_id: uuid.UUID = uuid.UUID(int=0)

    def parse(self, bgl_file_data: bytes, file_offset: int):
        super(FSXSceneryObjectHeader, self).parse(bgl_file_data, file_offset)
        (instance_id,) = struct.unpack(self.extra_fmt, bgl_file_data[file_offset + self.fmt_bytes_size:file_offset + self.fmt_bytes_size + 16])
        self.instance_id = uuid.UUID(bytes_le=instance_id)

    @property
    def total_size(self) -> int:
        return self.fmt_bytes_size + struct.calcsize(self.extra_fmt)

    def __str__(self):
        return f"[FSX SceneryObject Header] {self.__class__.__name__}"


class PlaceholderSceneryObjectHeader(SceneryObjectHeader):
    fmt = "@2H"

    def parse(self, bgl_file_data: bytes, file_offset: int):
        (self.id, self.size) = self.get_data(bgl_file_data, file_offset)

    @property
    def total_size(self) -> int:
        return self.fmt_bytes_size

    def __str__(self):
        return f"[FSX SceneryObject PlaceholderHeader] {self.__class__.__name__}"


class SceneryObjectRecord(Unpackable):
    header_type: type(SceneryObjectHeader) = None

    def __init__(self):
        super(SceneryObjectRecord, self).__init__()
        self.header: SceneryObjectHeader = self.header_type()
        self.data_offset: int = 0

    def parse(self, bgl_file_data: bytes, file_offset: int):
        self.header.parse(bgl_file_data, file_offset)
        self.data_offset: int = file_offset + self.header.total_size

    @property
    def total_size(self) -> int:
        return self.header.size

    def __str__(self):
        return f"{self.__class__.__name__} ({self.header.size} bytes)"


class FSXTaxiwaySign(SceneryObjectRecord):
    """ Airport taxiway signs container record """
    header_type = FSXSceneryObjectHeader
    fmt = '@L'

    def __init__(self):
        super(FSXTaxiwaySign, self).__init__()
        self.taxiway_signs_count: int = 0
        self.items: List[TaxiwaySignDataItem] = []

    def parse(self, bgl_file_data: bytes, file_offset: int):
        super(FSXTaxiwaySign, self).parse(bgl_file_data, file_offset)
        (self.taxiway_signs_count,) = self.get_data(bgl_file_data, self.data_offset)
        current_record_offset: int = self.data_offset + self.fmt_bytes_size
        for i in range(0, self.taxiway_signs_count):
            item: TaxiwaySignDataItem = TaxiwaySignDataItem(self.header.lon_raw_value, self.header.lat_raw_value)
            item.parse(bgl_file_data, current_record_offset)
            self.items.append(item)
            current_record_offset += item.total_size


class TaxiwaySignDataItem(Unpackable):
    """ Single taxiway sign """
    fmt = '@2fH2B'  # partial, variable size label string after this

    def __init__(self,
                 anchor_lon_raw_value: float,
                 anchor_lat_raw_value: float):
        super(TaxiwaySignDataItem, self).__init__()
        self.text_size: int = 0
        self.lon: float = 0.0
        self.lat: float = 0.0
        self.hdg: float = 0.0
        self.justification: TaxiwaySignJustification = TaxiwaySignJustification.LEFT
        self.label_raw_size: int = 0
        self.label: str = ""
        self.anchor_lon_raw_value: float = anchor_lon_raw_value
        self.anchor_lat_raw_value: float = anchor_lat_raw_value

    def parse(self, bgl_file_data: bytes, file_offset: int):
        fields = self.get_data(bgl_file_data, file_offset)
        (lon_offset_raw_value,
         lat_offset_raw_value,
         hdg,
         self.text_size,
         justification) = fields
        self.lat = parse_latitude((lat_offset_raw_value * 360) / EARTH_POLAR_CIRCUMFERENCE_M + self.anchor_lat_raw_value)
        lat_correction_factor = math.cos(math.radians(abs(self.anchor_lat_raw_value + lat_offset_raw_value / 2)))
        self.lon = parse_longitude((lon_offset_raw_value * 360) / (EARTH_EQUATORIAL_CIRCUMFERENCE_M * lat_correction_factor) + self.anchor_lon_raw_value)
        self.hdg = parse_pbh_value(hdg)
        self.justification = TaxiwaySignJustification(justification)
        self.label_raw_size, self.label = read_stringz_word_aligned(bgl_file_data[file_offset + self.fmt_bytes_size:])

    @property
    def total_size(self) -> int:
        return self.fmt_bytes_size + self.label_raw_size


class FS9TaxiwaySign(FSXTaxiwaySign):
    header_type = FS9SceneryObjectHeader


class LibraryObject(Unpackable):
    """ Library object info """
    fmt = '@16sf'

    def __init__(self):
        super(LibraryObject, self).__init__()
        self.name: uuid.UUID = uuid.UUID(int=0)
        self.scale: float = 1.0

    def parse(self, bgl_file_data: bytes, file_offset: int):
        (name,
         self.scale) = self.get_data(bgl_file_data, file_offset)
        self.name = uuid.UUID(bytes_le=name)

    def __str__(self):
        return f"{self.name} (scale: {self.scale})"


class FSXAttachedObjectData(Unpackable):
    fmt = '@8H3f16s2H'

    def __init__(self):
        super(FSXAttachedObjectData, self).__init__()
        self.id: int = 0
        self.start_delimiter_size: int = 4
        self.object_type_id: int = 0
        self.attached_object_data_size: int = 0
        self.attach_point_string_relative_offset: int = 0
        self.pitch: float = 0.0
        self.bank: float = 0.0
        self.hdg: float = 0.0
        self.bias_x: float = 0.0
        self.bias_y: float = 0.0
        self.bias_z: float = 0.0
        self.instance_id: uuid.UUID = uuid.UUID(int=0)
        self.obj_data: Optional[Union[LibraryObject, Beacon]] = None
        self.attach_point_name: str = ""
        self.closing_delimiter_id: int = 0
        self.closing_delimiter_size: int = 4

    def parse(self, bgl_file_data: bytes, file_offset: int):
        (self.id,
         self.start_delimiter_size,  # always 4
         self.object_type_id,
         self.attached_object_data_size,  # includes the attachpoint string
         self.attach_point_string_relative_offset,
         pitch,
         bank,
         hdg,
         self.bias_x,
         self.bias_y,
         self.bias_z,
         instance_id,  # TODO: FS9 version differs only by these last 3 fields, extract
         self.probability,
         self.randomness) = self.get_data(bgl_file_data, file_offset)
        self.pitch = parse_pbh_value(pitch)
        self.bank = parse_pbh_value(bank)
        self.hdg = parse_pbh_value(hdg)
        self.instance_id = uuid.UUID(bytes_le=instance_id)

        fixed_part_size = struct.calcsize(self.fmt)
        attached_obj_data_offset: int = file_offset + fixed_part_size
        if self.object_type_id in [SceneryObjectRecordType.FS9_LIB_OBJ, SceneryObjectRecordType.FSX_LIB_OBJ]:
            obj = LibraryObject()
            obj.parse(bgl_file_data, attached_obj_data_offset)
            self.obj_data = obj
        elif self.object_type_id in [SceneryObjectRecordType.FS9_BEACON, SceneryObjectRecordType.FSX_BEACON]:
            obj = Beacon()
            obj.parse(bgl_file_data, attached_obj_data_offset)
            self.obj_data = obj
        else:
            raise Exception(f"Unknown attached object type {hex(self.object_type_id)}")

        _, self.attach_point_name = read_stringz_word_aligned(bgl_file_data[file_offset + self.start_delimiter_size + self.attach_point_string_relative_offset:])

        # 3rd record, just id and size
        end_delimiter_offset = file_offset + self.start_delimiter_size + self.attached_object_data_size
        (self.closing_delimiter_id,
         self.closing_delimiter_size) = struct.unpack("@2H", bgl_file_data[end_delimiter_offset:end_delimiter_offset + 4])

        if self.closing_delimiter_id != 0x1003:
            raise Exception(f"attachedObject closing delimiter id is {self.closing_delimiter_id}")

    @property
    def total_size(self) -> int:
        return self.start_delimiter_size + self.attached_object_data_size + self.closing_delimiter_size

    def __str__(self):
        return f"FSX Attached Object type {hex(self.object_type_id)} instance id {self.instance_id} attached on '{self.attach_point_name}'"


class FS9AttachedObjectData(Unpackable):
    fmt = '@8H3f'

    def __init__(self):
        super(FS9AttachedObjectData, self).__init__()
        self.id: int = 0
        self.start_delimiter_size: int = 4
        self.object_type_id: int = 0
        self.attached_object_data_size: int = 0
        self.attach_point_string_relative_offset: int = 0
        self.pitch: float = 0.0
        self.bank: float = 0.0
        self.hdg: float = 0.0
        self.bias_x: float = 0.0
        self.bias_y: float = 0.0
        self.bias_z: float = 0.0
        self.obj_data: Optional[Union[LibraryObject, Beacon]] = None
        self.attach_point_name: str = ""
        self.closing_delimiter_id: int = 0
        self.closing_delimiter_size: int = 4

    def parse(self, bgl_file_data: bytes, file_offset: int):
        (self.id,
         self.start_delimiter_size,  # always 4
         self.object_type_id,
         self.attached_object_data_size,  # includes the attachpoint string
         self.attach_point_string_relative_offset,
         pitch,
         bank,
         hdg,
         self.bias_x,
         self.bias_y,
         self.bias_z,) = self.get_data(bgl_file_data, file_offset)
        self.pitch = parse_pbh_value(pitch)
        self.bank = parse_pbh_value(bank)
        self.hdg = parse_pbh_value(hdg)
        fixed_part_size = struct.calcsize(self.fmt)
        attached_obj_data_offset: int = file_offset + fixed_part_size
        if self.object_type_id in [SceneryObjectRecordType.FS9_LIB_OBJ, SceneryObjectRecordType.FSX_LIB_OBJ]:
            obj = LibraryObject()
            obj.parse(bgl_file_data, attached_obj_data_offset)
            self.obj_data = obj
        elif self.object_type_id in [SceneryObjectRecordType.FS9_BEACON, SceneryObjectRecordType.FSX_BEACON]:
            obj = Beacon()
            obj.parse(bgl_file_data, attached_obj_data_offset)
            self.obj_data = obj
        else:
            raise Exception(f"Unknown attached object type {hex(self.object_type_id)}")

        _, self.attach_point_name = read_stringz_word_aligned(bgl_file_data[file_offset + self.start_delimiter_size + self.attach_point_string_relative_offset:])

        # 3rd record, just id and size
        end_delimiter_offset = file_offset + self.start_delimiter_size + self.attached_object_data_size
        (self.closing_delimiter_id,
         self.closing_delimiter_size) = struct.unpack("@2H", bgl_file_data[end_delimiter_offset:end_delimiter_offset + 4])

        if self.closing_delimiter_id != 0x1001:
            raise Exception(f"attachedObject closing delimiter id is {self.closing_delimiter_id:04X}")

    @property
    def total_size(self) -> int:
        return self.start_delimiter_size + self.attached_object_data_size + self.closing_delimiter_size

    def __str__(self):
        return f"FS9 Attached Object type {hex(self.object_type_id)} attached on '{self.attach_point_name}'"


# NOTE: bias is encoded in the original coordinates, no additional fields
class LibraryObjectRecord(SceneryObjectRecord):
    """ Library object placement (FSX) """
    header_type = FSXSceneryObjectHeader
    fmt = '@16sf'  # unused but left for size calculation
    attached_object_delimiter_id: int = 0x1002
    attached_object_class: type(FSXAttachedObjectData) = FSXAttachedObjectData

    def __init__(self):
        super(LibraryObjectRecord, self).__init__()
        self.obj_info: LibraryObject = LibraryObject()
        self.attached_object: Optional[FSXAttachedObjectData] = None

    def parse(self, bgl_file_data: bytes, file_offset: int):
        super(LibraryObjectRecord, self).parse(bgl_file_data, file_offset)
        _ = self.get_data(bgl_file_data, file_offset)
        self.obj_info.parse(bgl_file_data, self.data_offset)
        next_record_offset = self.data_offset + self.fmt_bytes_size
        next_record_first_2_bytes = bgl_file_data[next_record_offset:next_record_offset + 2]
        if next_record_first_2_bytes:
            (next_id,) = struct.unpack("@H", next_record_first_2_bytes)
            if next_id == self.attached_object_delimiter_id:
                self.attached_object = self.attached_object_class()
                self.attached_object.parse(bgl_file_data, next_record_offset)

    def __str__(self):
        return f"{self.__class__.__name__} {self.obj_info}"

    @property
    def total_size(self) -> int:
        result = self.header.size
        if self.attached_object:
            result += self.attached_object.total_size
        return result


class FSXLibraryObjectRecord(LibraryObjectRecord):
    attached_object_delimiter_id: int = 0x1002
    attached_object_class: type(FSXAttachedObjectData) = FSXAttachedObjectData
    header_type = FSXSceneryObjectHeader


class FS9LibraryObjectRecord(LibraryObjectRecord):
    attached_object_delimiter_id: int = 0x1000
    attached_object_class: type(FSXAttachedObjectData) = FS9AttachedObjectData
    header_type = FS9SceneryObjectHeader


class Beacon(Unpackable):
    fmt = '@2BH'

    def __init__(self):
        super(Beacon, self).__init__()
        self.beacon_type: BeaconType = BeaconType.CIVILIAN_AIRPORT
        self.unknown_always_1: int = 1
        self.unknown_always_0: int = 0

    def parse(self, bgl_file_data: bytes, file_offset: int):
        fields = self.get_data(bgl_file_data, file_offset)
        (beacon_type,
         self.unknown_always_1,
         self.unknown_always_0) = fields
        self.beacon_type = BeaconType(beacon_type)

    def __str__(self):
        return f"{self.beacon_type.name} Beacon"


class FSXBeaconRecord(SceneryObjectRecord):
    header_type = FSXSceneryObjectHeader
    fmt = '@2BH'

    def __init__(self):
        super(FSXBeaconRecord, self).__init__()
        self.obj: Beacon = Beacon()

    def parse(self, bgl_file_data: bytes, file_offset: int):
        super(FSXBeaconRecord, self).parse(bgl_file_data, file_offset)
        self.obj.parse(bgl_file_data, self.data_offset)

    def __str__(self):
        return f"[FSX] {self.obj}"


class FS9BeaconRecord(FSXBeaconRecord):
    header_type = FS9SceneryObjectHeader

    def __str__(self):
        return f"[FS9] {self.obj}"


class FSXWindSock(SceneryObjectRecord):
    header_type = FSXSceneryObjectHeader
    fmt = '@2f4s4sH'

    def __init__(self):
        super(FSXWindSock, self).__init__()

    def parse(self, bgl_file_data: bytes, file_offset: int):
        super(FSXWindSock, self).parse(bgl_file_data, file_offset)
        (self.pole_height,
         self.sock_length,
         self.pole_rgba,
         self.sock_rgba,
         self.flag_lighted) = self.get_data(bgl_file_data, self.data_offset)

    def __str__(self):
        return f"Windsock (height={self.pole_height})"


class FS9WindSock(FSXWindSock):
    header_type = FS9SceneryObjectHeader


class FSXEffectPlacement(SceneryObjectRecord):
    header_type = FSXSceneryObjectHeader
    fmt = '@80s'  # partial, variable size effect_params string after this

    def __init__(self):
        super(FSXEffectPlacement, self).__init__()
        self.effect_name: str = ""
        self.effect_params: str = ""

    def parse(self, bgl_file_data: bytes, file_offset: int):
        super(FSXEffectPlacement, self).parse(bgl_file_data, file_offset)
        fields = self.get_data(bgl_file_data, self.data_offset)
        (effect_name_buffer,) = fields
        _, self.effect_name = read_stringz_word_aligned(effect_name_buffer)
        params_offset = self.data_offset + self.fmt_bytes_size
        effect_params_buffer_size = self.header.size - self.fmt_bytes_size
        effect_params_buffer = bgl_file_data[params_offset:params_offset + effect_params_buffer_size]
        self.effect_params = read_stringz(effect_params_buffer)

    def __str__(self):
        result: str = f" {self.effect_name}"
        if self.effect_params:
            result += f" ({self.effect_params})"
        return super(FSXEffectPlacement, self).__str__() + result


class FS9EffectPlacement(FSXEffectPlacement):
    header_type = FS9SceneryObjectHeader


class FSXPlaceHolderRecord(SceneryObjectRecord):
    header_type = FSXSceneryObjectHeader


class FS9PlaceHolderRecord(SceneryObjectRecord):
    header_type = FS9SceneryObjectHeader


class FSXGenericBuildingRecord(FSXPlaceHolderRecord):
    header_type = FSXSceneryObjectHeader
    # TODO


class FS9GenericBuildingRecord(FS9PlaceHolderRecord):
    header_type = FS9SceneryObjectHeader
    # TODO


class FSXTriggerRecord(FSXPlaceHolderRecord):
    header_type = FSXSceneryObjectHeader
    # TODO


class FS9TriggerRecord(FS9PlaceHolderRecord):
    header_type = FS9SceneryObjectHeader
    # TODO


class ExtrusionBridgeRecord(SceneryObjectRecord):
    fmt = "@16s16s3L3L2f2BH"
    header_type = FSXSceneryObjectHeader

    def __init__(self):
        super(ExtrusionBridgeRecord, self).__init__()
        self.profile: uuid.UUID = uuid.UUID(int=0)
        self.material_set: uuid.UUID = uuid.UUID(int=0)
        self.altitude_sample_location_1_lat: int = 0
        self.altitude_sample_location_1_lon: int = 0
        self.altitude_sample_location_1_alt: int = 0
        self.altitude_sample_location_2_lat: int = 0
        self.altitude_sample_location_2_lon: int = 0
        self.altitude_sample_location_2_alt: int = 0
        self.road_width: int = 0
        self.probability: int = 0
        self.suppress: int = 0
        self.placement_count: int = 0
        self.point_count: int = 0
        self.placements: List[uuid.UUID] = []
        self.points: List[Tuple[float, float, int]] = []

    def parse(self, bgl_file_data: bytes, file_offset: int):
        super(ExtrusionBridgeRecord, self).parse(bgl_file_data, file_offset)
        (profile,
         material_set,
         self.altitude_sample_location_1_lat,  # int32[3]
         self.altitude_sample_location_1_lon,
         self.altitude_sample_location_1_alt,
         self.altitude_sample_location_2_lat,  # int32[3]
         self.altitude_sample_location_2_lon,
         self.altitude_sample_location_2_alt,
         self.road_width,
         self.probability,
         self.suppress,
         self.placement_count,
         self.point_count,) = self.get_data(bgl_file_data, self.data_offset)
        self.profile: uuid.UUID = uuid.UUID(bytes_le=profile)
        self.material_set: uuid.UUID = uuid.UUID(bytes_le=material_set)

        placements_offset: int = self.data_offset + self.fmt_bytes_size
        placement_format: str = "@16s"
        placement_size: int = struct.calcsize(placement_format)
        for i in range(0, self.placement_count):
            current_offset = placements_offset + (i * placement_size)
            self.placements.append(*struct.unpack(placement_format, bgl_file_data[current_offset:current_offset + placement_size]))

        point_format: str = "@3L"
        point_size: int = struct.calcsize(point_format)
        points_offset = placements_offset + (self.placement_count * placement_size)
        for i in range(0, self.point_count):
            current_offset = points_offset + (i * point_size)
            point_lon, point_lat, point_alt = struct.unpack(point_format, bgl_file_data[current_offset:current_offset + point_size])
            self.points.append(
                (
                    parse_longitude(point_lon),
                    parse_latitude(point_lat),
                    point_alt
                )
            )

    def __str__(self):
        return super(ExtrusionBridgeRecord, self).__str__() + f" {self.placement_count} placements, {self.point_count} points"


class SceneryObjectRecordType(IntEnum):
    UNKNOWN = 0
    FS9_GENERIC_BUILDING = 0x01
    FS9_LIB_OBJ = 0x02
    FS9_WINDSOCK = 0x03
    FS9_FX = 0x04
    FS9_TAXIWAY_SIGN = 0x05
    FS9_TRIGGER = 0x07
    FS9_BEACON = 0x08
    # FS9_EXTRUSION_BRIDGE = 0x09 # ?
    FSX_GENERIC_BUILDING = 0x0A
    FSX_LIB_OBJ = 0x0B
    FSX_WINDSOCK = 0x0C
    FSX_FX = 0x0D
    FSX_TAXIWAY_SIGN = 0x0E
    FSX_TRIGGER = 0x10
    FSX_BEACON = 0x11
    FSX_EXTRUSION_BRIDGE = 0x12


SCENERYOBJECTS_IDS: Dict[int, Type[SceneryObjectRecord]] = {
    SceneryObjectRecordType.FS9_GENERIC_BUILDING.value: FS9GenericBuildingRecord,
    SceneryObjectRecordType.FS9_LIB_OBJ.value: FS9LibraryObjectRecord,
    SceneryObjectRecordType.FS9_WINDSOCK.value: FS9WindSock,
    SceneryObjectRecordType.FS9_FX.value: FS9EffectPlacement,
    SceneryObjectRecordType.FS9_TAXIWAY_SIGN.value: FS9TaxiwaySign,
    SceneryObjectRecordType.FS9_TRIGGER.value: FS9TriggerRecord,
    SceneryObjectRecordType.FS9_BEACON.value: FS9BeaconRecord,
    SceneryObjectRecordType.FSX_GENERIC_BUILDING.value: FSXGenericBuildingRecord,
    SceneryObjectRecordType.FSX_LIB_OBJ.value: LibraryObjectRecord,
    SceneryObjectRecordType.FSX_WINDSOCK.value: FSXWindSock,
    SceneryObjectRecordType.FSX_FX.value: FSXEffectPlacement,
    SceneryObjectRecordType.FSX_TAXIWAY_SIGN.value: FSXTaxiwaySign,
    SceneryObjectRecordType.FSX_TRIGGER.value: FSXTriggerRecord,
    SceneryObjectRecordType.FSX_BEACON.value: FSXBeaconRecord,
    SceneryObjectRecordType.FSX_EXTRUSION_BRIDGE.value: ExtrusionBridgeRecord,
}
