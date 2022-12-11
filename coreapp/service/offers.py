from typing import Dict, List
from dataclasses import dataclass
import uuid as uuid
from django.db.models import F, Value
from django.db.models.functions import Concat

from coreapp.models import Offer


class OfferFace:
    @staticmethod
    def get_offer_by_art(article, brand=None) -> List[Dict]:
        filter_payload = dict(product__article__art=article)
        if brand:
            filter_payload['product__brand__name'] = brand
        annotate_payload = dict(article=F('product__article__art'),
                                brand=F('product__brand__name'),
                                shop_name=F('shop__name'),
                                address=Concat('shop__city__name', Value(' '), 'shop__address'),
                                product_name=F('name'),
                                quantity=F('count'),
                                phone=F('shop__phone'))
        result = Offer.objects.filter(**filter_payload).annotate(**annotate_payload).values('name', 'article',
                                                                                            'brand', 'shop_name',
                                                                                            'address', 'phone',
                                                                                            'count', 'price',
                                                                                            'link__url')
        for item in result:
            item['link'] = item.pop('link__url')
        return list(result)
