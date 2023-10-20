import bs4
import requests
import subprocess
import sys
import regex


READ_MESSAGE = '{} read from input'
WRITTEN_MESSAGE = '{} written to output'
NAME_CLASS = 'name'
PARSER = 'html.parser'
SEARCH_URL = 'https://www.eliteprospects.com/search/player?q='
PROSPECTS_MEGATHREAD = 'https://forums.hfboards.com/threads/prospect-megathread.2764521/'

FULL_NAME_REGEX = r'(?b)(?:{}){{e<=2}}'

PROSPECTS_FILE = 'prospects.txt'
LINKS_FILE = 'links.txt'
LINK_FORMAT = '{} {} {}'

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
    hfboards_response = requests.get(PROSPECTS_MEGATHREAD)

    with open(PROSPECTS_FILE) as f:
        for index, line in enumerate(f.readlines()):

            if not line.strip():
                continue

            print(READ_MESSAGE.format(line.strip()))
            var = line.split()
            hf_link = get_hf_link(var, hfboards_response)
            ep_link = get_ep_link(var)

            link = LINK_FORMAT.format(line.strip(), ep_link, hf_link)
            links.append(LINK_FORMAT.format(line.strip(), format_link(ep_link, 'EP'),
                                            format_link(hf_link, 'HF')))

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


def get_hf_link(var, megathread):
    hfboards_soup = bs4.BeautifulSoup(megathread.content, PARSER)

    full_name = f'{var[1]} {var[2]}'

    res = scrape_from_page(hfboards_soup, 'a', 'class', 'link link--external',
                           string=regex.compile(FULL_NAME_REGEX.format(full_name)))

    if res:
        hf_url = res[0].attrs['href']
    else:
        hf_url = None
        print(f"HF BOARDS LINK for {full_name} NOT FOUND. Check that player's name is without typos !!!")

    return hf_url


def get_ep_link(var):
    query = f'{var[1]}+{var[2]}'
    response = requests.get(SEARCH_URL + query)
    soup = bs4.BeautifulSoup(response.content, PARSER)

    try:
        name_cell = scrape_from_page(soup, 'td', 'class', NAME_CLASS)[0]
    except IndexError:
        print('!!!!!!!!!! LINK NOT FOUND !!!!!!!!!')
        return

    url = name_cell.find('a').attrs['href']

    return url


if __name__ == '__main__':
    start_scraping()
