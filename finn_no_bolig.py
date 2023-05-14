# -*- coding: utf-8 -*-

from urllib.parse import urljoin
from scrape_tools import scrape_site
import re


SEARCH_URL_FILE = './in_out/finn_no.in'
APRTS_FILE = './in_out/finn_no.out'
HISTORY_FILE = './in_out/finn_no.history'

FINNNO_BASE_URL = 'https://www.finn.no/realestate/homes/search.html'
PUSHOVER_TOKEN = 'aototezet9b6mea31ys6gh3a76so49'


def main():
    scrape_site(get_elements, get_attrs, get_next_page, 'Finn.no (eiendom)', aprt_string_format,
                pushover_token=PUSHOVER_TOKEN, history_file=HISTORY_FILE,
                searches_file=SEARCH_URL_FILE, elmnts_out_file=APRTS_FILE)


def aprt_string_format(ad_link, search_link, ad_dict):
    return f'{ad_link} \n{ad_dict["cost"]} kr / {ad_dict["total_cost"]} kr\n{ad_dict["misc_info"]}'


def get_elements(page):
    return page.find('div', class_='ads').findAll('div', class_='relative', recursive=False)


def get_attrs(aprt, aprt_dict, search):
    link = aprt.find('a')
    aprt_id = link["id"]
    href = link["href"]

    viewing = ''
    try:
        viewing = aprt.select('span.inline-block.px-8')[0].getText(strip=True)
    except Exception:
        print("Could not fetch viewing date: " + href)
    if not viewing == 'Visning etter avtale':
        return aprt_dict

    title = aprt.find('h3').get_text(strip=True)
    address = aprt.find('span', class_='text-14 text-gray-500').get_text(strip=True)
    info_spans = aprt.find('div', class_='text-12').findAll('span')
    costs = info_spans[0].get_text('**', strip=True)
    misc_info = info_spans[2].get_text(strip=True)
    total_cost = re.search('(?<=Totalpris:\s)[^kr]*(?=(?:\s-\s)?)', costs)[0]

    main_info = aprt.select('div.col-span-2.mt-16')[0].findAll()
    cost = main_info[1].getText(strip=True)[:-2]
    size = main_info[0].getText(strip=True)

    aprt_dict[aprt_id] = dict(
        href=href,
        title=address,
        finn_title=title,
        address=address,
        cost=cost,
        total_cost=total_cost,
        size=size,
        misc_info=misc_info,
        search=search
    )

    return aprt_dict


def get_next_page(page, _page_url):
    next_page = page.find('a', class_='button button--pill button--has-icon button--icon-right')
    if not next_page:
        return None
    return urljoin(FINNNO_BASE_URL, next_page.attrs['href'])


if __name__ == '__main__':
    main()
