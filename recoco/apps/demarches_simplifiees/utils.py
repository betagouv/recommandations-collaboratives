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
    lookup: str | None = None


project_mapping_fields: list[MappingField] = [
    MappingField(
        id="project.name",
        label="Nom du projet",
        lookup="name",
    ),
    MappingField(
        id="project.first_name",
        label="Prénom du porteur du projet",
        lookup="owner.first_name",
    ),
    MappingField(
        id="project.last_name",
        label="Nom du porteur du projet",
        lookup="owner.first_name",
    ),
    MappingField(
        id="project.full_name",
        label="Nom complet du porteur du projet (Prénom + Nom)",
        lookup="owner.full_name",
    ),
    MappingField(
        id="project.reverse_full_name",
        label="Nom complet du porteur du projet (Nom + Prénom)",
        lookup="owner.full_name_reversed",
    ),
    MappingField(
        id="project.email",
        label="Email du porteur du projet",
        lookup="owner.email",
    ),
    MappingField(
        id="project.organization_position",
        label="Email du porteur du projet",
        lookup="owner.profile.organization_position",
    ),
    MappingField(
        id="project.phone_number",
        label="Téléphone du porteur du projet",
        lookup="owner.profile.phone_no.as_international",
    ),
    MappingField(
        id="project.insee",
        label="Code INSEE de la commune",
        lookup="commune.insee",
    ),
    MappingField(
        id="project.postal_code",
        label="Code postal de la commune",
        lookup="commune.postal",
    ),
    MappingField(
        id="project.department_code",
        label="Code du département",
        lookup="commune.department.code",
    ),
    MappingField(
        id="project.region_code",
        label="Code de la région",
        lookup="commune.department.region.code",
    ),
]
