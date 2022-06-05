from coreapp.models import Site, ParameterKey, SiteParameter
import requests
import logging

LOGGER = logging.getLogger(__name__)


class SiteFacade:
    """Фасад для работы с сайтом"""

    def __init__(self, site: Site):
        self.site = site

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
        headers = {
            'User-Agent':
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
        }
        # 'Mozilla/5.0(X11; Linux x86_64) AppleWebKit / 537.36(KHTML, like Gecko) Chrome / 102.0.5005.61 Safari/537.36'
        result_data_set = {'Disallow': [], 'Allow': [], 'Sitemap': [], 'Clean-param': []}

        result = requests.get(url, headers=headers)
        if result.status_code == 200:
            result = result.content.decode()
            result = result.replace('\r', '')
            for line in result.split("\n"):
                result = result.replace('\r', '')
                if line.startswith('Allow'):
                    result_data_set["Allow"].append(line.split(': ')[1].split(' ')[0])
                elif line.startswith('Disallow'):
                    result_data_set["Disallow"].append(line.split(': ')[1].split(' ')[0])
                elif line.startswith('Sitemap'):
                    result_data_set["Sitemap"].append(line.split(': ')[1].split(' ')[0])
                elif line.startswith('Clean-param'):
                    result_data_set["Clean-param"].append(line.split(': ')[1].split(' ')[0])
            for key, values in result_data_set.items():
                self.set_params(key, values)
            return True
        else:
            LOGGER.error(f"Error receiving robots.txt {result}")
