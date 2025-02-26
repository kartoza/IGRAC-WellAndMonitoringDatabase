"""Test ODS Reader."""

from gwml2.terms import SheetName
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

    def check(self, sheet_name):
        """Check."""
        self.assertTrue(
            sheet_name in SheetName().get_uploader(sheet_name).SHEETS,
        )

    def test_sheet_name(self):
        """To sheet name."""
        self.check(SheetName.general_information)
        self.check(SheetName.hydrogeology)
        self.check(SheetName.management)
        self.check(SheetName.drilling_and_construction)

        self.check(SheetName.water_strike)
        self.check(SheetName.stratigraphic_log)
        self.check(SheetName.structure)

        self.check(SheetName.groundwater_level)
        self.check(SheetName.groundwater_quality)
        self.check(SheetName.abstraction_discharge)
