import arrow

import utils


def main():
    # username = input("Enter user handle: ")
    username = "zahalgirls"
    source = utils.get_single_page(username)
    results = utils.parse_main_page(source)
    if not results:
        print('Profile not found')
        return

    if results['is_private']:
        print('Profile is private')
        return

    media = results['media']

    print('Downloading images...')
    count = 0
    while True:
        n = utils.get_images(media['edges'], username)

        print('%s/%s' % (count, media['count']))
        count += n

        max_id = media['edges'][-1]['node']['id']
        source = utils.get_single_page(username, max_id)
        media = utils.parse_single_page(source)

        has_next_page = media.get('page_info', {}).get('has_next_page', False)
        if not has_next_page:
            print('Done!')
            break


if __name__ == '__main__':
    """
        TODO list:
        * handle refused connection errors (retry M times with N second intervals)
        * write log to DL folder (errors, image description etc.)
    """
    main()
