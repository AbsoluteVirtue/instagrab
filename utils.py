import pathlib

import resources
import bs4_impl as dom_parser


def _get_user(doc):
    return doc['entry_data']['ProfilePage'][0]['graphql']['user']


def parse_main_page(html_source):
    profile_info = dom_parser.get_profile_json(html_source)
    try:
        user = _get_user(profile_info)
    except Exception as ex:
        print(ex)
        return {}

    data = {
        'is_private': user['is_private'],
        'media': user['edge_owner_to_timeline_media'],
        'profile_pic': user['profile_pic_url_hd'],
        'id': user['id'],
        'fb_page': user['connected_fb_page'],
    }
    return data


def parse_pic_page(html_source):
    pics_info = dom_parser.get_profile_json(html_source)
    data = {
        'media': pics_info['entry_data']['PostPage'][0]['graphql']['shortcode_media']['display_url'],
        'id': pics_info['entry_data']['PostPage'][0]['graphql']['shortcode_media']['id'],
        'user': pics_info['entry_data']['PostPage'][0]['graphql']['shortcode_media']['owner']['username'],
    }
    if pics_info['entry_data']['PostPage'][0]['graphql']['shortcode_media'].get('edge_sidecar_to_children'):
        data.update(
            children=[{
                'media': edge['node']['display_url'],
                'id': edge['node']['id'],
            } for edge in pics_info['entry_data']['PostPage'][0][
                'graphql']['shortcode_media']['edge_sidecar_to_children']['edges']])

    return data


async def get_single_page(session, url):
    response = await session.get(url=url)
    content = await response.text()
    return content


def parse_single_page(html_source):
    profile_info = dom_parser.get_profile_json(html_source)
    user = _get_user(profile_info)
    return user['edge_owner_to_timeline_media']


def _get_single_entries_list(nodes):
    result = []
    for node in nodes:
        n = node['node']
        if not n['is_video']:
            result.append({
                # 'code': n['code'],
                'thumbnail': n['thumbnail_src'],
                'pic': n['display_url'],
                # 'date': n['date'],
                'id': n['id'],
                'caption': n.get('caption', '')
            })

    return result


async def get_images(session, nodes, username, idx):
    entries = _get_single_entries_list(nodes)
    n = 0
    for entry in entries:
        result = await dl_image(session, entry['pic'], entry['id'], username, idx)
        if not result['success']:
            return None

        n += 1

    return n


async def dl_image(session, pic_url, pic_id, username, idx):
    response = await session.get(url=pic_url)
    if not response.status == 200:
        return {'success': False}

    content = await response.read()

    path_template = '%s%s'
    dirpath = resources.default_download_dir % (username, idx)
    pathlib.Path(dirpath).mkdir(parents=True, exist_ok=True)
    filepath = path_template % (
        dirpath,
        resources.filename_template.format(
            username=username, id=pic_id))
    with open(filepath, 'wb') as temp_file:
        temp_file.write(content)
        return {'success': True, 'file': filepath}


def _insert_exif_comment(jpg_file, date, caption):
    import piexif

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
