from typing import Dict, List

from coreapp.models import Offer


class OfferFace:
    @staticmethod
    def get_offer_by_art(article, brand=None) -> List[Dict]:
        payload = dict(product__article__art=article)
        if brand:
            payload['product__brand__name'] = brand
        result = Offer.objects.filter(**payload).values('name', 'count', 'price', 'link__url')
        return result
