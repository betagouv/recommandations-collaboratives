from django import template

register = template.Library()


@register.filter
def format_phone(phone_number):
    """
    Formats a phone number by adding spaces between every two digits.
    It replaces the +33 by 0 at the begining
    """
    phone_number = str(phone_number).replace(" ", "")
    if phone_number.startswith("+33"):
        phone_number = "0" + phone_number[3:]
    return " ".join(phone_number[i : i + 2] for i in range(0, len(phone_number), 2))
