import requests
import arrow
import pathlib

import resources
import bs4_impl as parser


def _get_user(doc):
    return doc['entry_data']['ProfilePage'][0]['user']


def get_profile_main_page_deprecated(user_handle):
    response = requests.get(url=resources.base_insta_url % user_handle)
    return response.content


def parse_main_page(html_source):
    profile_info = parser.get_profile_json(html_source)
    user = _get_user(profile_info)
    data = {
        'is_private': user['is_private'],
        'media': user['media'],
        'profile_pic': user['profile_pic_url_hd'],
        'id': user['id'],
        'fb_page': user['connected_fb_page'],
    }
    return data


def get_single_page(username, max_id=None):
    url = resources.base_insta_url % username
    if max_id:
        url += resources.next_page_insta_path % max_id
    response = requests.get(url)
    return response.content


def parse_single_page(html_source):
    profile_info = parser.get_profile_json(html_source)
    user = _get_user(profile_info)
    return user['media']


def _get_single_entries_list(nodes):
    result = []
    for node in nodes:
        if not node['is_video']:
            result.append({
                'code': node['code'],
                'thumbnail': node['thumbnail_src'],
                'pic': node['display_src'],
                'date': node['date'],
                'id': node['id'],
            })
    return result


def get_images(nodes, username):
    current_date = arrow.now().strftime("%Y-%m-%d")
    entries = _get_single_entries_list(nodes)
    for entry in entries:
        success = dl_image(entry['pic'], username, current_date, entry['date'])
        if not success:
            print('error DLing file')


def dl_image(url, username, date, timestamp):
    response = requests.get(url)
    if not response.status_code == 200:
        return False

    filepath = '%s%s'
    dirpath = resources.default_download_dir % username
    pathlib.Path(dirpath).mkdir(parents=True, exist_ok=True)
    with open(
            filepath % (
                    dirpath, resources.filename_template.format(
                        username=username,
                        date=date,
                        timestamp=timestamp
                    )
            )
            , 'wb'
    ) as temp_file:
        temp_file.write(response.content)
        return True
