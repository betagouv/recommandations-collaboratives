from allauth.socialaccount.providers.openid_connect import views as base_views


def login(request, provider_id):
    return base_views.login(request, provider_id)


def callback(request, provider_id):
    return base_views.callback(request, provider_id)
