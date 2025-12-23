"""
Schema
"""

from drf_spectacular.extensions import OpenApiAuthenticationExtension


class BrandAPIKeyAuthenticationScheme(OpenApiAuthenticationExtension):
    """
    Brand APIKey Authentication Scheme
    """

    target_class = "licenses.authentication.BrandAPIKeyAuthentication"
    name = "BrandApiKeyAuth"

    def get_security_definition(self, auto_schema):
        """
        get security definition
        """
        return {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-KEY",
            "description": "Brand API Key authentication",
        }
