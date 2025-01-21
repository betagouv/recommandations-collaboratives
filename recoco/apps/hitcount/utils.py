from django.contrib.contenttypes.models import ContentType
from django.db.models import Model


def ct_label(obj: Model) -> str:
    obj_content_type = ContentType.objects.get_for_model(obj)
    return f"{obj_content_type.app_label}.{obj_content_type.model}"


def ct_from_label(content_type: str) -> ContentType | None:
    try:
        app_label, model = content_type.split(".")
    except ValueError:
        return None
    if app_label and model:
        try:
            return ContentType.objects.get(app_label=app_label, model=model)
        except ContentType.DoesNotExist:
            return None
