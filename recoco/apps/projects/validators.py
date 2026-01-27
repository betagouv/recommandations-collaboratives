#!/usr/bin/env python

import puremagic
from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible


@deconstructible
class MimetypeValidator(object):
    def __init__(self, allows=None, forbids=None, code="file-type"):
        self.forbidden_mimetypes = forbids or []
        self.allowed_mimetypes = allows or []
        self.code = code

    def __call__(self, value):
        try:
            mime = puremagic.from_string(value.read(2048), mime=True)

            if (mime in self.forbidden_mimetypes) or (
                mime not in self.allowed_mimetypes
            ):
                raise ValidationError(
                    f"{value} n'est pas un fichier autorisé", code=self.code
                )

        except AttributeError as e:
            raise ValidationError(
                "Impossible d'évaluer le type de ficher", code=self.code
            ) from e
