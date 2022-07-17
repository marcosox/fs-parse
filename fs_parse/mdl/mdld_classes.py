import struct
from typing import Dict, List, Optional

from fs_parse.datatypes import DataValue, FixedSizeStruct, UnpackableBuffer
from fs_parse.mdl.classes import MDLSection, PlaceHolderMDLSection, RIFFSectionHeader
from fs_parse.mdl.constants import AlphaTestFunction, AnimationTransformationType, BlendType, MATERIAL_FLAGS_1, MATERIAL_FLAGS_2
from fs_parse.mdl.utils import get_material_flag_labels
from fs_parse.utils import stringz_2_ascii


class TEXTSection(MDLSection):
    """
    This section contains the list of all textures of the object.
    """
    texture_size = 64

    def __init__(self, header: RIFFSectionHeader):
        super().__init__(header)
        self.texture_names: List[str] = []

    def parse(self, mdl_file_data: bytes, file_offset: int):
        current_offset = file_offset
        while current_offset < file_offset + self.header.data_size:
            (texture_name,) = struct.unpack(f"{self.texture_size}s", mdl_file_data[current_offset:current_offset + self.texture_size])
            self.texture_names.append(stringz_2_ascii(texture_name))
            current_offset += self.texture_size


class MaterialItem(UnpackableBuffer):
    data_format = [
        FixedSizeStruct("9L16f3L2f")
    ]

    def __init__(self):
        self.material_flags: int = 0
        self.material_flags_labels: List[str] = []
        self.material_flags_2: int = 0
        self.material_flags_2_labels: List[str] = []
        self.diffuse_texture_index: int = 0
        self.detail_texture_index: int = 0
        self.bumpmap_texture_index: int = 0
        self.specular_texture_index: int = 0
        self.emissive_texture_index: int = 0
        self.reflection_texture_index: int = 0
        self.fresnel_texture_index: int = 0
        self.diffuse_color_R: float = 0.0
        self.diffuse_color_G: float = 0.0
        self.diffuse_color_B: float = 0.0
        self.diffuse_color_A: float = 0.0
        self.specular_color_R: float = 0.0
        self.specular_color_G: float = 0.0
        self.specular_color_B: float = 0.0
        self.specular_color_A: float = 0.0
        self.specular_power: float = 0.0
        self.detail_map_scale: float = 0.0
        self.bump_map_scale: float = 0.0
        self.reflection_scale: float = 0.0
        self.precipitation_offset: float = 0.0
        self.specular_map_power_scale: float = 0.0
        self.specular_bloom_floor: float = 0.0
        self.ambient_light_scale: float = 0.0
        self.source_blend: BlendType = BlendType.ZERO
        self.destination_blend: BlendType = BlendType.ZERO
        self.alpha_test_function: AlphaTestFunction = AlphaTestFunction.NEVER
        self.alpha_test_threshold: float = 0.0
        self.final_alpha_multiply: float = 0.0

    def parse(self, mdl_file_data: bytes, file_offset: int):
        (self.material_flags,
         self.material_flags_2,
         self.diffuse_texture_index,
         self.detail_texture_index,
         self.bumpmap_texture_index,
         self.specular_texture_index,
         self.emissive_texture_index,
         self.reflection_texture_index,
         self.fresnel_texture_index,
         self.diffuse_color_R,
         self.diffuse_color_G,
         self.diffuse_color_B,
         self.diffuse_color_A,
         self.specular_color_R,
         self.specular_color_G,
         self.specular_color_B,
         self.specular_color_A,
         self.specular_power,
         self.detail_map_scale,
         self.bump_map_scale,
         self.reflection_scale,
         self.precipitation_offset,
         self.specular_map_power_scale,
         self.specular_bloom_floor,
         self.ambient_light_scale,
         source_blend,
         destination_blend,
         alpha_test_function,
         self.alpha_test_threshold,
         self.final_alpha_multiply,) = self.get_data(mdl_file_data, file_offset)
        self.material_flags_labels = get_material_flag_labels(self.material_flags, MATERIAL_FLAGS_1)
        self.material_flags_2_labels = get_material_flag_labels(self.material_flags, MATERIAL_FLAGS_2)
        self.source_blend = BlendType(source_blend)
        self.destination_blend = BlendType(destination_blend)
        self.alpha_test_function = AlphaTestFunction(alpha_test_function)

    @property
    def size(self):
        return sum([dv.size for dv in self.data_format])

    def __str__(self):
        data = self.to_dict()
        props = ", ".join([f"{k}={v}" for k, v in data.items()])
        return f"{props}"

    def __repr__(self):
        return str(self)


class MATESection(MDLSection):
    """
    This section contains a list of all materials of the object.
    """

    def __init__(self, header: RIFFSectionHeader):
        super().__init__(header)
        self.items: List[MaterialItem] = []

    def parse(self, mdl_file_data: bytes, file_offset: int):
        current_offset = file_offset
        while current_offset < file_offset + self.header.data_size:
            item = MaterialItem()
            item.parse(mdl_file_data, current_offset)
            self.items.append(item)
            current_offset += item.size

    def __str__(self):
        return f"{self.header} ({len(self.items)} materials)"


class INDESection(MDLSection):
    """
    This section contains of a lot of triangles, each given by three short values.
    These values are the indices of the vertices to use.
    """

    def __init__(self, header: RIFFSectionHeader):
        super().__init__(header)
        self.triangles: List[tuple] = []

    def parse(self, mdl_file_data: bytes, file_offset: int):
        current_offset = file_offset
        triangle_fmt = "3H"
        triangle_size = struct.calcsize(triangle_fmt)
        while current_offset < file_offset + self.header.data_size:
            triangle = struct.unpack(triangle_fmt, mdl_file_data[current_offset:current_offset + triangle_size])
            self.triangles.append(triangle)
            current_offset += triangle_size

    def __str__(self):
        return f"{self.header} ({len(self.triangles)} triangles)"


class VERBSection(MDLSection):
    """
    This section gives the vertex buffer of the object.
    """

    def parse(self, mdl_file_data: bytes, file_offset: int):
        pass  # TODO: 4 subsections


class TRANSection(MDLSection):
    """
    This section stores the static transformation matrices.
    """

    def __init__(self, header: RIFFSectionHeader):
        super().__init__(header)
        self.matrices: List[tuple] = []

    def parse(self, mdl_file_data: bytes, file_offset: int):
        current_offset = file_offset
        matrix_fmt = "16f"
        matrix_size = struct.calcsize(matrix_fmt)
        while current_offset < file_offset + self.header.data_size:
            matrix = struct.unpack(matrix_fmt, mdl_file_data[current_offset:current_offset + matrix_size])
            self.matrices.append(matrix)
            current_offset += matrix_size

    def __str__(self):
        return f"{self.header} ({len(self.matrices)} matrices)"


class AnimationItem(UnpackableBuffer):
    data_format = [
        FixedSizeStruct("2L")
    ]

    def __init__(self):
        super(AnimationItem, self).__init__()
        self.transformation_type = AnimationTransformationType
        self.tran_section: int = 0

    def parse(self, mdl_file_data: bytes, file_offset: int):
        (transformation_type, self.tran_section) = self.get_data(mdl_file_data, file_offset)
        self.transformation_type = AnimationTransformationType(transformation_type)


class AMAPSection(MDLSection):
    """
    This section contains animation map data.
    """

    def __init__(self, header: RIFFSectionHeader):
        super().__init__(header)
        self.items: List[AnimationItem] = []

    def parse(self, mdl_file_data: bytes, file_offset: int):
        current_offset = file_offset
        while current_offset < file_offset + self.header.data_size:
            item = AnimationItem()
            item.parse(mdl_file_data, current_offset)
            self.items.append(item)
            current_offset += item.size

    def __str__(self):
        return f"{self.header} ({len(self.items)} animation items)"


class SCENSection(MDLSection):
    """
    This section defines the scenegraph. This is refered to from the PART section.
    """

    def parse(self, mdl_file_data: bytes, file_offset: int):
        pass  # TODO


class SGALSection(MDLSection):
    """
    This is the scenegraph animation linkage section.
    """

    def parse(self, mdl_file_data: bytes, file_offset: int):
        pass  # TODO


class SGVLSection(MDLSection):
    """
    This is the scenegraph visibility linkage section.
    """

    def parse(self, mdl_file_data: bytes, file_offset: int):
        pass  # TODO


class SGJCSection(MDLSection):
    """
    This scenegraph section contains IK joint constraint data.
    """

    def parse(self, mdl_file_data: bytes, file_offset: int):
        pass  # TODO


class SGBRSection(MDLSection):
    """
    This is the scenegraph bone reference section.
    """

    def parse(self, mdl_file_data: bytes, file_offset: int):
        pass  # TODO


class LODTSection(MDLSection):
    """
    This section defines the LOD table of the object.
    It is followed by a LODE section for each LOD level in the object.
    """

    def parse(self, mdl_file_data: bytes, file_offset: int):
        pass  # TODO


class ANIBSection(MDLSection):
    """
    Animation block section.
    """

    def parse(self, mdl_file_data: bytes, file_offset: int):
        pass  # TODO


class PLALSection(MDLSection):
    """
    Platform list. Contains a number of PLAT entries.
    """

    def parse(self, mdl_file_data: bytes, file_offset: int):
        pass  # TODO


class REFLSection(MDLSection):
    """
    Attachpoint list. Contains a number of REFP entries.
    """

    def parse(self, mdl_file_data: bytes, file_offset: int):
        pass  # TODO


class ATTOSection(MDLSection):
    """
    The ATTO section defines the attached objects and relates them to a certain attachpoint (by name).
    """

    def parse(self, mdl_file_data: bytes, file_offset: int):
        pass  # TODO


class VISLSection(MDLSection):
    """
    Unknown
    """

    def parse(self, mdl_file_data: bytes, file_offset: int):
        pass  # TODO


class MDLDSection(MDLSection):
    """
    This section contains the actual data defining the object.
    """
    data_format: List[DataValue] = []

    metadata_only_exclude: List[str] = [
        "INDE",
        "VERB",
        "TRAN",
        "ANIB",
    ]
    section_types: Dict[str, type(MDLSection)] = {
        "TEXT": TEXTSection,
        "MATE": MATESection,
        "INDE": INDESection,
        "VERB": VERBSection,
        "TRAN": TRANSection,
        "AMAP": AMAPSection,
        "SCEN": SCENSection,
        "SGAL": SGALSection,
        "SGVL": SGVLSection,
        "SGJC": SGJCSection,
        "SGBR": SGBRSection,
        "LODT": LODTSection,
        "ANIB": ANIBSection,
        "PLAL": PLALSection,
        "REFL": REFLSection,
        "ATTO": ATTOSection,
        "VISL": VISLSection,
        "MREC": PlaceHolderMDLSection,  # unknown section found in the aerosoft F16 containing xml gauge code?
        "MREI": PlaceHolderMDLSection,  # unknown section found in the aerosoft F16
    }

    def __init__(self, header: RIFFSectionHeader, metadata_only: bool = False):
        super().__init__(header)
        self.metadata_only: bool = metadata_only
        self.text: Optional[TEXTSection] = None
        self.mate: Optional[MATESection] = None
        self.inde: Optional[INDESection] = None
        self.verb: Optional[VERBSection] = None
        self.tran: Optional[TRANSection] = None
        self.amap: Optional[AMAPSection] = None
        self.scen: Optional[SCENSection] = None
        self.sgal: Optional[SGALSection] = None
        self.sgvl: Optional[SGVLSection] = None
        self.sgjc: Optional[SGJCSection] = None
        self.sgbr: Optional[SGBRSection] = None
        self.lodt: Optional[LODTSection] = None
        self.anib: Optional[ANIBSection] = None
        self.plal: Optional[PLALSection] = None
        self.refl: Optional[REFLSection] = None
        self.atto: Optional[ATTOSection] = None
        self.visl: Optional[VISLSection] = None
        self.mrec: Optional[PlaceHolderMDLSection] = None
        self.mrei: Optional[PlaceHolderMDLSection] = None

    def parse(self, mdl_file_data: bytes, file_offset: int):
        current_offset = file_offset
        while current_offset < (file_offset + self.header.data_size):
            header = RIFFSectionHeader()
            header.parse(mdl_file_data, current_offset)
            current_offset += 8
            section_name = header.type_id.lower()
            if header.type_id in self.section_types:
                section = self.section_types[header.type_id](header)
                if (not self.metadata_only) or (header.type_id not in self.metadata_only_exclude):
                    section.parse(mdl_file_data, current_offset)
                else:
                    self._logger.debug(f"Skipping parsing of {header.type_id} section since self.metadata_only is set")
                if isinstance(getattr(self, section_name), list):
                    getattr(self, section_name).append(section)
                else:
                    setattr(self, section_name, section)
            else:
                raise Exception(f"Unknown section {header.type_id} at offset {current_offset}")
            current_offset += header.data_size
