"""
Licenses Apps
"""

from django.apps import AppConfig


class LicensesConfig(AppConfig):
    """
    Licenses Config
    """

    name = "licenses"

    def ready(self):
        """
        Ready
        """
        import licenses.schema  # pylint: disable=unused-import, import-outside-toplevel
