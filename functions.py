from gwml2.harvesters.models.harvester import (
    Harvester, HarvesterLog, RUNNING, DONE
)


class Functions:
    """Class that contains some functions."""

    def restart_harvesters(self):
        """Restart harvester by removing running status and logs."""
        HarvesterLog.objects.filter(status=RUNNING).update(status=DONE)
        Harvester.objects.filter(is_run=True).update(is_run=False)
