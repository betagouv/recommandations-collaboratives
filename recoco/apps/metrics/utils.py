from django.conf import settings
from django.db.models import Case, CharField, F, TextField, Value, When
from django.db.models.functions import MD5, Cast, Concat


def hash_field(name: str, salt: str = ""):
    """Use a part of the secret key as a stable salt to generate a hash of the given field"""
    partial_secret = settings.SECRET_KEY[:10]
    salt += partial_secret
    return MD5(Cast(Concat(F(name), Value(salt)), TextField()))


def display_value(choices, field):
    options = [When(**{field: k, "then": Value(v)}) for k, v in choices]
    return Case(*options, output_field=CharField())
