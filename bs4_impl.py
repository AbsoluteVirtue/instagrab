from bs4 import BeautifulSoup
from bs4.diagnose import diagnose
import re
import json
import settings


"""
    path: soup.contents[5].contents[5].text
"""


def get_profile_json(html_source):
    soup = BeautifulSoup(html_source, settings.config.get('parser', 'html.parser'))

    if settings.config.get('debug'):
        diagnose(html_source)

    content = soup.find(type='text/javascript', string=re.compile('window._sharedData'))
    # TODO: check for content and handle exception to skip the pic and advance to next
    shared_data = content.string.strip().replace('window._sharedData = ', '')[:-1]
    result = {}
    try:
        result = json.loads(shared_data)
    except Exception:
        pass

    return result


def get_pic_url(html_source):
    soup = BeautifulSoup(html_source, settings.config.get('parser', 'html.parser'))

    if settings.config.get('debug'):
        diagnose(html_source)

    content = soup.find('meta', content=re.compile("https://instagram"))
    return content.attrs.get('content')
