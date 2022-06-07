from coreapp.models import Site, ParameterKey, SiteParameter, Url
from urllib.parse import urlparse
import logging

LOGGER = logging.getLogger(__name__)


class SiteFacade:
    """Фасад для работы с сайтом"""

    def __init__(self, site: Site):
        self.site = site
        self.url = site.url

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

    def create_urls(self, urlset):
        for url_loc in urlset:
            Url.objects.get_or_create(link=url_loc.findNext("loc").text,
                                      site=self.site,
                                      defaults={'link': url_loc.findNext("loc").text, 'site': self.site})

    def get_urls(self, keys: list):
        keys = ParameterKey.objects.filter(title__in=keys)
        urls = list(self.site.parameters.filter(key__in=keys).values_list('value', flat=True))
        return urls

    def get_domain(self):
        return urlparse(self.url).netloc

    def clear_urls(self):
        self.site.urls.all().delete()
