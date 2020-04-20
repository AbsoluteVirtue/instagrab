from bs4 import BeautifulSoup
import re
import json


def get_profile_json(html_source):
    """
        path: soup.contents[5].contents[5].text
        default parser: html5lib
    """
    soup = BeautifulSoup(html_source, 'lxml')
    content = soup.find(type='text/javascript', string=re.compile('window._sharedData'))
    # TODO: check for content and handle exception to skip the pic and advance to next
    shared_data = content.string.strip().replace('window._sharedData = ', '')[:-1]
    result = {}
    try:
        result = json.loads(shared_data)
    except Exception:
        pass

    return result


def get_pic_json(html_source):
    soup = BeautifulSoup(html_source, 'lxml')
    content = soup.find(type='text/javascript', string=re.compile('window._sharedData'))
    return json.loads(content)
