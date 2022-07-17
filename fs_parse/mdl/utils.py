from typing import Dict, List, Union

from fs_parse.mdl.constants import MaterialFlags1, MaterialFlags2


def get_material_flag_labels(val: int, mapping: Dict[int, Union[MaterialFlags1, MaterialFlags2]]) -> List[str]:
    result = []
    for mask, label in mapping.items():
        if val & mask != 0:
            result.append(label.value)
    return result
