from hijack.permissions import superusers_and_staff


def superusers_and_staff_but_not_bots(*, hijacker, hijacked):
    """Same as hijack's superusers_and_staff, except nobody can hijack a bot:
    a bot only authenticates with its API key, never with a session.
    """
    if hijacked is not None and hijacked.profile.is_bot:
        return False
    return superusers_and_staff(hijacker=hijacker, hijacked=hijacked)
