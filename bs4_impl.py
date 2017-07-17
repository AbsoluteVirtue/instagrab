from bs4 import BeautifulSoup
import re
import ujson


def get_profile_json(html_source):
    """
        soup.contents[5].contents[5].text
    """
    soup = BeautifulSoup(html_source, 'lxml')
    content = soup.find(type='text/javascript', string=re.compile('window._sharedData'))
    shared_data = content.string.strip().replace('window._sharedData = ', '')[:-1]
    return ujson.loads(shared_data)
