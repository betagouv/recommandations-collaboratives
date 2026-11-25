from drf_spectacular.extensions import OpenApiAuthenticationExtension


class ServiceAPIKeyScheme(OpenApiAuthenticationExtension):
    """Show service API keys as a login method in the OpenAPI schema"""

    target_class = "recoco.apps.api_keys.authentication.ServiceAPIKeyAuthentication"
    name = "serviceApiKey"

    def get_security_definition(self, auto_schema):
        return {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": "Clé d'API d'un compte de service : `Api-Key <clé>`",
        }
