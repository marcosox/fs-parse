from enum import IntEnum

from fs_parse.bgl.constants import StrEnum


class MaterialFlags1(StrEnum):
    MATERIAL_IS_SPECULAR = "Material is specular"
    MATERIAL_HAS_A_DIFFUSE_TEXTURE = "Material has a diffuse texture (diffuse color is only used as a fallback)"
    MATERIAL_HAS_A_BUMPMAP_TEXTURE = "Material has a bumpmap texture"
    MATERIAL_HAS_A_SPECULAR_TEXTURE = "Material has a specular texture"
    MATERIAL_HAS_A_DETAIL_TEXTURE = "Material has a detail texture"
    MATERIAL_HAS_A_REFLECTION_TEXTURE = "Material has a reflection texture"
    USE_GLOBAL_ENVIRONMENT_MAP_AS_REFLECTION = "Use global environment map as reflection"
    MATERIAL_HAS_AN_EMISSIVE_TEXTURE = "Material has an emissive texture (for night)"
    MATERIAL_HAS_A_FRESNELRAMP_TEXTURE_REFLECTION = "Material has a FresnelRamp texture: Reflection"
    MATERIAL_HAS_A_FRESNELRAMP_TEXTURE_DIFFUSE = "Material has a FresnelRamp texture: Diffuse"
    MATERIAL_HAS_A_FRESNELRAMP_TEXTURE_SPECULAR = "Material has a FresnelRamp texture: Specular"
    APPLY_OFFSET_TO_START_OF_PRECIPITATION = "Apply offset to start of Precipitation"
    TAKE_INTO_ACCOUNT_PRECIPITATION = "Take into account Precipitation"
    BLEND_ENVIRONMENT_BY_INVERSE_OF_DIFFUSE_ALPHA = "Blend environment by inverse of diffuse alpha"
    BLEND_ENVIRONMENT_BY_SPECULAR_MAP_ALPHA = "Blend environment by specular map alpha"
    ASSUME_VERTICAL_NORMAL = "Assume vertical normal"
    Z_WRITE_ALPHA = "Z-Write alpha"
    NO_Z_WRITE = "No Z Write"
    BLOOM_MATERIAL_BY_COPYING = "Bloom material by copying"
    BLOOM_MATERIAL_MODULATING_BY_ALPHA = "Bloom material modulating by alpha"
    VOLUME_SHADOW = "Volume shadow"
    NO_SHADOW = "No shadow"
    Z_TEST_ALPHA = "Z-Test Alpha"
    EMISSIVE_MODE_BLEND = "Emissive Mode: Blend"
    SET_FINAL_ALPHA_VALUE_AT_RENDER_TIME = "Set final alpha value at render time"
    SKINNED_MESH = "Skinned mesh"
    ALLOW_BLOOM = "Allow bloom"
    ALLOW_EMISSIVE_BLOOM = "Allow emissive bloom"
    BLEND_DIFFUSE_BY_DIFFUSE_ALPHA = "Blend diffuse by diffuse alpha"
    BLEND_DIFFUSE_BY_INVERSE_OF_SPECULAR_MAP_ALPHA = "Blend diffuse by inverse of specular map alpha"
    PRELIT_VERTICES = "Prelit vertices"


class MaterialFlags2(StrEnum):
    BLEND_CONSTANT = "Blend constant"
    FORCE_TEXTURE_ADDRESS_WRAP = "Force Texture Address Wrap"
    FORCE_TEXTURE_ADDRESS_CLAMP = "Force Texture Address Clamp"
    DOUBLE_SIDED = "Double sided"
    EMISSIVE_MODE_ADDITIVENIGHTONLYUSERCONTROLLED = "Emissive Mode: AdditiveNightOnlyUserControlled"
    EMISSIVE_MODE_BLENDUSERCONTROLLED = "Emissive Mode: BlendUserControlled"
    EMISSIVE_MODE_MULTIPLYBLEND = "Emissive Mode: MultiplyBlend"
    EMISSIVE_MODE_MULTIPLYBLENDUSERCONTROLLED = "Emissive Mode: MultiplyBlendUserControlled"
    EMISSIVE_MODE_ADDITIVE = "Emissive Mode: Additive"
    EMISSIVE_MODE_ADDITIVEUSERCONTROLLED = "Emissive Mode: AdditiveUserControlled"


MATERIAL_FLAGS_1 = {
    0x00000001: MaterialFlags1.MATERIAL_IS_SPECULAR,
    0x00000002: MaterialFlags1.MATERIAL_HAS_A_DIFFUSE_TEXTURE,
    0x00000004: MaterialFlags1.MATERIAL_HAS_A_BUMPMAP_TEXTURE,
    0x00000008: MaterialFlags1.MATERIAL_HAS_A_SPECULAR_TEXTURE,
    0x00000010: MaterialFlags1.MATERIAL_HAS_A_DETAIL_TEXTURE,
    0x00000020: MaterialFlags1.MATERIAL_HAS_A_REFLECTION_TEXTURE,
    0x00000040: MaterialFlags1.USE_GLOBAL_ENVIRONMENT_MAP_AS_REFLECTION,
    0x00000080: MaterialFlags1.MATERIAL_HAS_AN_EMISSIVE_TEXTURE,
    0x00000100: MaterialFlags1.MATERIAL_HAS_A_FRESNELRAMP_TEXTURE_REFLECTION,
    0x00000200: MaterialFlags1.MATERIAL_HAS_A_FRESNELRAMP_TEXTURE_DIFFUSE,
    0x00000400: MaterialFlags1.MATERIAL_HAS_A_FRESNELRAMP_TEXTURE_SPECULAR,
    0x00000800: MaterialFlags1.APPLY_OFFSET_TO_START_OF_PRECIPITATION,
    0x00001000: MaterialFlags1.TAKE_INTO_ACCOUNT_PRECIPITATION,
    0x00002000: MaterialFlags1.BLEND_ENVIRONMENT_BY_INVERSE_OF_DIFFUSE_ALPHA,
    0x00004000: MaterialFlags1.BLEND_ENVIRONMENT_BY_SPECULAR_MAP_ALPHA,
    0x00008000: MaterialFlags1.ASSUME_VERTICAL_NORMAL,
    0x00010000: MaterialFlags1.Z_WRITE_ALPHA,
    0x00020000: MaterialFlags1.NO_Z_WRITE,
    0x00040000: MaterialFlags1.BLOOM_MATERIAL_BY_COPYING,
    0x00080000: MaterialFlags1.BLOOM_MATERIAL_MODULATING_BY_ALPHA,
    0x00100000: MaterialFlags1.VOLUME_SHADOW,
    0x00200000: MaterialFlags1.NO_SHADOW,
    0x00400000: MaterialFlags1.Z_TEST_ALPHA,
    0x00800000: MaterialFlags1.EMISSIVE_MODE_BLEND,
    0x01000000: MaterialFlags1.SET_FINAL_ALPHA_VALUE_AT_RENDER_TIME,
    0x04000000: MaterialFlags1.SKINNED_MESH,
    0x08000000: MaterialFlags1.ALLOW_BLOOM,
    0x10000000: MaterialFlags1.ALLOW_EMISSIVE_BLOOM,
    0x20000000: MaterialFlags1.BLEND_DIFFUSE_BY_DIFFUSE_ALPHA,
    0x40000000: MaterialFlags1.BLEND_DIFFUSE_BY_INVERSE_OF_SPECULAR_MAP_ALPHA,
    0x80000000: MaterialFlags1.PRELIT_VERTICES,
}
MATERIAL_FLAGS_2 = {
    0x00000001: MaterialFlags2.BLEND_CONSTANT,
    0x00000002: MaterialFlags2.FORCE_TEXTURE_ADDRESS_WRAP,
    0x00000004: MaterialFlags2.FORCE_TEXTURE_ADDRESS_CLAMP,
    0x00000008: MaterialFlags2.DOUBLE_SIDED,
    0x00000010: MaterialFlags2.EMISSIVE_MODE_ADDITIVENIGHTONLYUSERCONTROLLED,
    0x00000020: MaterialFlags2.EMISSIVE_MODE_BLENDUSERCONTROLLED,
    0x00000040: MaterialFlags2.EMISSIVE_MODE_MULTIPLYBLEND,
    0x00000080: MaterialFlags2.EMISSIVE_MODE_MULTIPLYBLENDUSERCONTROLLED,
    0x00000100: MaterialFlags2.EMISSIVE_MODE_ADDITIVE,
    0x00000200: MaterialFlags2.EMISSIVE_MODE_ADDITIVEUSERCONTROLLED,
}


class BlendType(IntEnum):
    ZERO = 1
    ONE = 2
    SRCCOLOR = 3
    INVSRCCOLOR = 4
    SRCALPHA = 5
    INVSRCALPHA = 6
    DESTALPHA = 7
    INVDESTALPHA = 8
    DESTCOLOR = 9
    INVDESTCOLOR = 10


class AlphaTestFunction(IntEnum):
    NEVER = 1
    LESS = 2
    EQUAL = 3
    LESSEQUAL = 4
    GREATER = 5
    NOTEQUAL = 6
    GREATEREQUAL = 7
    ALWAYS = 8


class AnimationTransformationType(IntEnum):
    STATIC_NODE = 1
    ANIMATED_NODE = 2
