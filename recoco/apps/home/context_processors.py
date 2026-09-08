from django.http import HttpRequest


def embed(request: HttpRequest) -> dict:
    return {"is_embedded": getattr(request, "is_embedded", False)}
