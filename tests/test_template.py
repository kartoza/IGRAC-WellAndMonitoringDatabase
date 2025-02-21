"""Test ODS Reader."""

from gwml2.tests.base import GWML2Test
from igrac.models.site_preference import SitePreference


class TemplateTest(GWML2Test):
    """Test templates."""

    def test_script(self):
        """To file exist."""
        pref = SitePreference.objects.first()
        if not pref:
            pref, _ = SitePreference.objects.get_or_create()

        self.assertTrue(pref.wells_sync)
        self.assertTrue(pref.monitoring_data_sync)
        self.assertTrue(pref.drilling_and_construction_sync)
