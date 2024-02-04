import random
import string

def generate_random_id(start: str = ""):
    """
    Generates a random alphabetic id.
    """
    result = "".join(random.SystemRandom().choices(string.ascii_lowercase, k=16))
    if start:
        result = "-".join([start, result])
    return result

