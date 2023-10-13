from django.core.management.base import BaseCommand

from gwml2.models.upload_session import UploadSession


class Command(BaseCommand):
    """ Run all harvester
    """
    true_str = ['true', 'y', 'yes']

    def add_arguments(self, parser):
        parser.add_argument(
            '-id',
            '--id',
            dest='id',
            default='',
            help='ID of upload session')

    def handle(self, *args, **options):
        id = options.get('id', None)

        if id:
            queryset = UploadSession.objects.filter(id=int(id))
        else:
            queryset = UploadSession.objects.all()

        for upload in queryset:
            upload.create_report_excel()
