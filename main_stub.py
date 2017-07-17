import utils


def main():
    # uh = input("Enter user handle: ")
    source = utils.get_profile_main_page('brojaq')
    parse_results = utils.parse_main_page(source)
    print(parse_results['is_private'])


if __name__ == '__main__':
    main()
