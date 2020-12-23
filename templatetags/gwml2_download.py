import json
from django import template

register = template.Library()


@register.simple_tag
def get_download_session_info(download_session):
    """ return info of download session """
    return '\n'.join([
        '{} : {}'.format(key, value) for key, value in json.loads(download_session.filters.replace('\'', '"')).items()
    ])
