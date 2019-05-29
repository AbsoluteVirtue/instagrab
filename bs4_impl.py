from bs4 import BeautifulSoup
import re
import json


def get_profile_json(html_source):
    """
        soup.contents[5].contents[5].text
    """
    soup = BeautifulSoup(html_source, 'lxml')
    content = soup.find(type='text/javascript', string=re.compile('window._sharedData'))
    # TODO: check for content and handle exception to skip the pic and advance to next
    shared_data = content.string.strip().replace('window._sharedData = ', '')[:-1]
    return json.loads(shared_data)
