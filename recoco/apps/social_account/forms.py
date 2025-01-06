from allauth.socialaccount.forms import SignupForm as SocialSignupForm


class SignupForm(SocialSignupForm):
    field_order = [
        "first_name",
        "last_name",
        "organization",
        "organization_position",
        "email",
        "phone_no",
        "captcha",
    ]
