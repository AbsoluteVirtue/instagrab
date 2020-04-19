import aiohttp.web
import aiohttp_jinja2
import uuid
from urllib import parse

from resources import base_insta_url, next_page_insta_path, pic_insta_url
import utils
from . import Base


class Input(Base):

    async def get(self):

        response = aiohttp_jinja2.render_template('home.html', self.request, context={})
        return response

    async def post(self):
        req_text = await self.request.text()

        for _, links in parse.parse_qs(req_text).items():
            for username in links:
                url = base_insta_url % username

                source = await utils.get_single_page(self.request.app['http'], url)
                results = utils.parse_main_page(source)
                if not results:
                    self.request.app['logger'].error('Profile not found')
                    continue

                if results['is_private']:
                    self.request.app['logger'].error('Profile is private')
                    continue

                media = results['media']

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


class Single(Base):

    async def get(self):
        _id = self.request.match_info['id']
        url = pic_insta_url % _id

        source = await utils.get_single_page(self.request.app['http'], url)
        results = utils.parse_pic_page(source)
        if results.get('children'):
            for child in results['children']:
                img_res = await utils.dl_image(self.request.app['http'],
                                               child['media'], child['id'], results['user'], _id)
        else:
            img_res = await utils.dl_image(self.request.app['http'],
                                           results['media'], results['id'], results['user'], _id)

        location = self.request.app.router['home'].url_for()
        raise aiohttp.web.HTTPFound(location=location)
