from bs4 import BeautifulSoup

from coreapp.models import Site, ParameterKey, SiteParameter, Url
import requests
import logging


LOGGER = logging.getLogger(__name__)


class SiteFacade:
    """Фасад для работы с сайтом"""

    def __init__(self, site: Site):
        self.site = site
        self.user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                          'Chrome/50.0.2661.102 Safari/537.36'
        # 'Mozilla/5.0(X11; Linux x86_64) AppleWebKit / 537.36(KHTML, like Gecko) Chrome / 102.0.5005.61 Safari/537.36'
        self.headers = {'User-Agent': self.user_agent}

    def set_params(self, key, values: list):
        key, _ = ParameterKey.objects.get_or_create(title=key, defaults={'title': key})
        key.save()
        if key.title == 'Clean-param':
            for value in values:
                vals = value.split('&')
                for val in vals:
                    param, _ = SiteParameter.objects.get_or_create(key=key, value=val, site=self.site,
                                                                   defaults={'key': key, 'value': val,
                                                                             'site': self.site})
        else:
            for val in values:
                param, _ = SiteParameter.objects.get_or_create(key=key, value=val, site=self.site,
                                                               defaults={'key': key, 'value': val, 'site': self.site})

    def read_robots(self):
        url = f'{self.site.url}/robots.txt'
        result_data_set = dict()
        result = requests.get(url, headers=self.headers)
        if result.status_code == 200:
            result = result.content.decode()
            result = result.replace('\r', '')
            for line in result.split("\n"):
                result = result.replace('\r', '')
                key = line.split(': ')[0].split(' ')[0]
                value = line.split(': ')[1].split(' ')[0]
                if key not in result_data_set.keys():
                    result_data_set[key] = list()
                result_data_set[key].append(value)
            for key, values in result_data_set.items():
                self.set_params(key, values)
            return True
        else:
            LOGGER.error(f"Error receiving robots.txt {result}")
            return False

    def process_sitemap(self, soup):
        urlset = soup.find_all("url")
        for url_loc in urlset:
            Url.objects.get_or_create(link=url_loc.findNext("loc").text,
                                      site=self.site,
                                      defaults={'link': url_loc.findNext("loc").text, 'site': self.site})
        sitemap_tags = soup.find_all("sitemap")
        for sitemap in sitemap_tags:
            url = sitemap.findNext("loc").text
            result = requests.get(url, headers=self.headers)
            if result.status_code == 200:
                soup = BeautifulSoup(result.content, features='xml')
                self.process_sitemap(soup)
            else:
                LOGGER.error(f"Error receiving sitemap {result}")
            break

    def read_sitemap(self):
        keys = ParameterKey.objects.filter(title__in=('Sitemap', 'sitemap'))
        urls = list(self.site.parameters.filter(key__in=keys).values_list('value', flat=True))
        for url in urls:
            result = requests.get(url, headers=self.headers)
            if result.status_code == 200:
                soup = BeautifulSoup(result.content, features='xml')
                self.process_sitemap(soup)
            else:
                LOGGER.error(f"Error receiving sitemap {result}")
                return False
