import aiohttp.web
import aiohttp_jinja2
import uuid
from urllib import parse

from resources import base_insta_url, next_page_insta_path, pic_insta_url
import utils
from . import Base


class Main(Base):

    async def _get_img_links(self, url):
        source = await utils.get_single_page(self.request.app['http'], url)
        results = utils.parse_main_page(source)
        if not results:
            self.request.app['logger'].error('Profile not found')
            return None

        if results['is_private']:
            self.request.app['logger'].error('Profile is private')
            return None

        return results['media']

    async def get(self):
        username = self.request.match_info['name']

        media = await self._get_img_links(base_insta_url % username)

        children = [edge['node']['display_url'] for edge in media['edges']]

        response = aiohttp_jinja2.render_template('pic.html', self.request, context={
            'data': {
                'children': children,
                'user': username,
                'id': '---',
            },
        })
        return response

    async def post(self):
        req_text = await self.request.text()

        for _, links in parse.parse_qs(req_text).items():
            for username in links:
                url = base_insta_url % username

                media = await self._get_img_links(url)

                self.request.app['logger'].info('Downloading images...')
                count = 0
                idx = uuid.uuid4().hex
                while True:
                    n = await utils.get_images(self.request.app['http'],
                                               media['edges'], username, idx)
                    if not n:
                        continue

                    count += n
                    self.request.app['logger'].info('%s/%s' % (count, media['count']))

                    url += next_page_insta_path % media['edges'][-1]['node']['id']

                    source = await utils.get_single_page(self.request.app['http'], url)
                    media = utils.parse_single_page(source)

                    has_next_page = media.get('page_info', {}).get('has_next_page', False)
                    if not has_next_page:
                        break

        location = self.request.app.router['home'].url_for()
        raise aiohttp.web.HTTPFound(location=location)


class SinglePost(Base):

    async def get(self):
        _id = self.request.match_info['id']
        url = pic_insta_url % _id

        source = await utils.get_single_page(self.request.app['http'], url)
        results = utils.parse_pic_page(source)

        children = [results['media']]
        children.extend([child['media'] for child in results.get('children', [])])

        response = aiohttp_jinja2.render_template('pic.html', self.request, context={
            'data': {
                'children': children,
                'user': results['user'],
                'id': _id,
            }
        })
        return response
