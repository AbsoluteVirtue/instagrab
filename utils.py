import requests
import arrow
import pathlib
import piexif

import resources
import bs4_impl as parser


def _get_user(doc):
    return doc['entry_data']['ProfilePage'][0]['user']


def get_profile_main_page_deprecated(user_handle):
    response = requests.get(url=resources.base_insta_url % user_handle)
    return response.content


def parse_main_page(html_source):
    profile_info = parser.get_profile_json(html_source)
    try:
        user = _get_user(profile_info)
    except Exception:
        return {}
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
                'caption': node.get('caption', '')
            })
    return result


def get_images(nodes, username):
    current_date = arrow.now()
    entries = _get_single_entries_list(nodes)

    n = 0
    for entry in entries:
        result = dl_image(entry['pic'], username, current_date, entry['date'])
        if not result['success']:
            print('error DLing file')
        n += 1

    return n


def dl_image(url, username, date, timestamp):
    response = requests.get(url)
    if not response.status_code == 200:
        return {'success': False}

    path_template = '%s%s'
    dirpath = resources.default_download_dir % (username, date.strftime("%Y-%m-%d"))
    pathlib.Path(dirpath).mkdir(parents=True, exist_ok=True)
    filepath = path_template % (
                    dirpath,
                    resources.filename_template.format(
                        username=username,
                        date=_get_date_string_from_timestamp(timestamp),
                        timestamp=timestamp
                    )
            )
    with open(filepath, 'wb') as temp_file:
        temp_file.write(response.content)
        return {'success': True, 'file': filepath}


def _get_date_string_from_timestamp(timestamp):
    r = str(arrow.get(timestamp))
    return r.split('+')[0].replace(':', '-')


def _insert_exif_comment(jpg_file, date, caption):
    exif_dict = piexif.load(jpg_file)
    exif_dict.pop("thumbnail")
    if not exif_dict['Exif'] and caption:
        exif_dict['Exif'] = {
            piexif.ExifIFD.DateTimeOriginal: date.strftime("%Y:%m:%d %H:%M:%S"),
            piexif.ExifIFD.UserComment: caption.encode('utf-8'),
            piexif.ExifIFD.LensMake: u"LensMake",
            piexif.ExifIFD.Sharpness: 65535,
            piexif.ExifIFD.LensSpecification: ((1, 1), (1, 1), (1, 1), (1, 1)),
        }
    try:
        exif_bytes = piexif.dump(exif_dict)
        piexif.insert(exif_bytes, jpg_file)

        from PIL import Image
        i = Image.open(jpg_file)
        i.save(jpg_file, exif=exif_bytes)
    except ValueError:
        return False
    else:
        return True
