from django.db.models import QuerySet
from coreapp.models import Product
import logging

LOGGER = logging.getLogger(__name__)


class ProuctFace:
    """Фасад для поиска товаров и предложений"""

    @staticmethod
    def get_products(self, request: str) -> QuerySet:
        products = Product.objects.filter(article__art__icontains=request)
        return products
