import bs4
import requests
import subprocess
import sys
import re


READ_MESSAGE = '{} read from input'
WRITTEN_MESSAGE = '{} written to output'
NAME_CLASS = 'name'
PARSER = 'html.parser'
SEARCH_URL = 'https://www.eliteprospects.com/search/player?q='
PROSPECTS_MEGATHREAD = 'https://forums.hfboards.com/threads/prospect-megathread.2764521/'
PROSPECTS_FILE = 'prospects.txt'
LINKS_FILE = 'links.txt'
LINK_FORMAT = '[url={}]{}[/url]'

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
    links = []

    with open(PROSPECTS_FILE) as f:
        for index, line in enumerate(f.readlines()):
            if not line.strip():
                continue

            print(READ_MESSAGE.format(line.strip()))
            var = line.split()
            query = f'{var[1]}+{var[2]}'
            response = requests.get(SEARCH_URL + query, headers=headers)
            soup = bs4.BeautifulSoup(response.content, PARSER)

            try:
                name_cell = scrape_from_page(soup, 'td', 'class', NAME_CLASS)[0]
            except IndexError:
                print('!!!!!!!!!! LINK NOT FOUND !!!!!!!!!')
                continue

            url = name_cell.find('a').attrs['href']
            links.append(LINK_FORMAT.format(url, line.strip()))

    with open(LINKS_FILE, 'w') as f:
        for index, link in enumerate(links):
            f.write(link + '\n')
            print(WRITTEN_MESSAGE.format(link))

    open_file(LINKS_FILE)


if __name__ == '__main__':
    start_scraping()
