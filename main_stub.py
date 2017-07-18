
import utils


def main():
    # uh = input("Enter user handle: ")
    username = 'brojaq'
    source = utils.get_single_page(username)
    results = utils.parse_main_page(source)
    if results['is_private']:
        print('Profile is private')
        return

    media = results['media']

    print('Downloading images...')
    while True:
        utils.get_images(media['nodes'], username)

        max_id = media['nodes'][-1]['id']
        source = utils.get_single_page(username, max_id)
        media = utils.parse_single_page(source)

        has_next_page = media.get('page_info', {}).get('has_next_page', False)
        if not has_next_page:
            print('Done!')
            break


if __name__ == '__main__':
    main()
