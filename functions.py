from gwml2.models.upload_session import UploadSession


class Functions:
    """Class that contains some functions."""

    def restart_harvesters(self):
        """Restart harvester by removing running status and logs."""
        pass

    def restart_uploads(self):
        """Restart uploads."""
        for upload in UploadSession.objects.filter(
                task_id__isnull=False
        ).filter(
            is_processed=False
        ).filter(
            is_canceled=False
        ):
            upload.run_in_background()
