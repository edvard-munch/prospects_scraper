import bs4
import enchant
import regex
import requests
import subprocess
import sys


READ_MESSAGE = '{} read from input'
WRITTEN_MESSAGE = '{} written to output'
NAME_CLASS = 'name'
PARSER = 'html.parser'

RESOURCES = [
    'ELITEPROSPECTS',
    'HFBOARDS'
]

EP_AUTOCOMPLETE_URL = 'https://autocomplete.eliteprospects.com/all?q={}&hideNotActiveLeagues=1'
EB_BASE_PLAYER_LINK = 'https://www.eliteprospects.com/player/{}/{}'
PROSPECTS_MEGATHREAD = 'https://forums.hfboards.com/threads/prospect-megathread.2764521/'

REGEX_ERRORS_LIMIT = 2 # with 3 it gives wrong results too often
NAME_REGEX = r'\w* \w*'
FULL_NAME_REGEX = r'(?b)(?:{}){{e<={}}}'

PROSPECTS_FILE = 'prospects.txt'
PROPER_NAMES_FILE = 'names'
LINKS_FILE = 'links.txt'

NOT_FOUND_MESSAGE = "{} LINK for {} NOT FOUND. Check that player's name is without typos !!!"

PLATFORMS = {
    'Windows': 'win32',
    'Mac_OS': 'darwin',
}

FILE_OPENERS = {
    'Linux': 'xdg-open',
    'Mac_OS': 'open'
}


def open_file(filename):
    if sys.platform == PLATFORMS['Windows']:
        os.startfile(filename)
    else:
        if sys.platform == PLATFORMS['Mac_OS']:
            opener = FILE_OPENERS['Mac_OS']
        else:
            opener = FILE_OPENERS['Linux']

        subprocess.call([opener, filename])


def scrape_from_page(soup, element_type, attr_type, attr_name, string=None):
    return soup.find_all(element_type, {attr_type: attr_name}, string=string)


def start_scraping():
    names_dictionary = enchant.pypwl.PyPWL('names.txt')
    links = []
    hfboards_response = requests.get(PROSPECTS_MEGATHREAD)

    with open(PROSPECTS_FILE) as f:
        for index, line in enumerate(f.readlines()):

            line = line.strip()
            if not line:
                continue

            print(READ_MESSAGE.format(line))
            query_name = regex.search(NAME_REGEX, line)[0]

            hf_link = get_hf_link(query_name, hfboards_response)
            ep_link = get_ep_link(query_name, names_dictionary)

            link = f"{line}, {format_link(ep_link, 'EP')}, {format_link(hf_link, 'HF')}"
            links.append(link)

    with open(LINKS_FILE, 'w') as f:
        for index, link in enumerate(links):
            f.write(link + '\n')
            print(WRITTEN_MESSAGE.format(link))

    open_file(LINKS_FILE)


def format_link(link, text):
    if link:
        return f'[url={link}]{text}[/url]'
    else:
        return text


def get_hf_link(query_name, megathread):
    hfboards_soup = bs4.BeautifulSoup(megathread.content, PARSER)
    res = scrape_from_page(hfboards_soup, 'a', 'class', 'link link--external',
                           string=regex.compile(FULL_NAME_REGEX.format(query_name, REGEX_ERRORS_LIMIT)))

    if res:
        hf_url = res[0].attrs['href']
    else:
        hf_url = None
        print(NOT_FOUND_MESSAGE.format(RESOURCES[1], query_name))

    return hf_url


def get_ep_link(query_name, names_dictionary):
    data = request_player_EP(query_name)

    if data:
        id_, slug, fullname = data[0]['id'], data[0]['slug'], data[0]['fullname']

    else:
        suggestions = names_dictionary.suggest(query_name)
        if suggestions:
            data = request_player_EP(suggestions[0])
            if data:
                id_, slug, fullname = data[0]['id'], data[0]['slug'], data[0]['fullname']
            else:
                print(NOT_FOUND_MESSAGE.format(RESOURCES[0], query_name))
                return
        else:
            print(NOT_FOUND_MESSAGE.format(RESOURCES[0], query_name))
            return

    url = EB_BASE_PLAYER_LINK.format(id_, slug)

    if not names_dictionary.is_added(fullname):
        names_dictionary.add(fullname)

    return url


def request_player_EP(query_name):
    response = requests.get(EP_AUTOCOMPLETE_URL.format(query_name))
    return response.json()


if __name__ == '__main__':
    start_scraping()
