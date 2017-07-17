import requests

import resources
import bs4_impl as parser


def get_profile_main_page(user_handle):
    response = requests.get(url=resources.base_insta_url % user_handle)
    return response.content


def parse_main_page(html_source):
    profile_info = parser.get_profile_json(html_source)
    user = _get_user(profile_info)
    media = user['media']
    data = {
        'is_private': user['is_private'],
        'single_entries': _get_single_entries_list(media),
        'profile_pic': user['profile_pic_url_hd'],
        'id': user['id'],
        'fb_page': user['connected_fb_page'],
    }
    return data


def _get_user(doc):
    return doc['entry_data']['ProfilePage'][0]['user']


def _get_single_entries_list(media):
    result = []
    for node in media['nodes']:
        if not node['is_video']:
            result.append({
                'code': node['code'],
                'thumbnail': node['thumbnail_src'],
                'pic': node['display_src'],
                'date': node['date'],
            })
    return result
