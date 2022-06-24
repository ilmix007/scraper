from typing import List

from django.db.models import QuerySet
from coreapp.models import Product
import logging

from mqttapp.models import ProductResult

LOGGER = logging.getLogger(__name__)


class ProuctFace:
    """Фасад для поиска товаров и предложений"""

    @staticmethod
    def get_products(request: str) -> List[ProductResult]:
        result = list()
        for prod in Product.objects.filter(article__art__icontains=request):
            result.append(ProductResult(name=prod.name, art=prod.article, brand=prod.brand))
        return result
