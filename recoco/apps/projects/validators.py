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
            # filename is only used to distinguish same header mime types
            mime = puremagic.from_string(
                value.read(2048), mime=True, filename=value.name
            )

            if (mime in self.forbidden_mimetypes) or (
                mime not in self.allowed_mimetypes
            ):
                raise ValidationError(
                    f"{value} n'est pas un fichier autorisé", code=self.code
                )

        except puremagic.main.PureError:
            return "text/plain"

            # puremagic does not detect mime if no header until v2 that needs python 3.12 or later

            # raise ValidationError(
            #     "Impossible d'évaluer le type de ficher", code=self.code
            # ) from e
