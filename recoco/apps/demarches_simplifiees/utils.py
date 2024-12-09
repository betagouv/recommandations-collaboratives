import hashlib
import json
from dataclasses import dataclass
from typing import Any


def hash_data(data: dict[str, Any]) -> str:
    s_data = json.dumps(data, sort_keys=True).encode("utf-8")
    return hashlib.sha256(s_data).hexdigest()


@dataclass
class MappingField:
    id: str
    label: str


project_mapping_fields: list[MappingField] = [
    MappingField(id="project.name", label="Nom du projet"),
]
