import csv, json, io
from typing import Iterable, Dict, Any
from django.db import transaction
from .models import Shop, Category, Product, ProductInfo, Parameter, \
    ProductParameter


class ProductImporter:
    def __init__(self, shop_name: str | None = None):
        self.shop_name = shop_name

    @transaction.atomic
    def import_stream(self, fbytes: bytes, filename: str) -> int:
        name = filename.lower()
        if name.endswith(".csv"):
            reader = csv.DictReader(io.StringIO(fbytes.decode("utf-8")))
            return self._import_rows(reader)
        elif name.endswith(".json"):
            data = json.loads(fbytes.decode("utf-8"))
            if isinstance(data, dict):
                rows = data.get("items") or data.get("products") or []
            else:
                rows = data
            return self._import_rows(rows)
        else:
            raise ValueError("Поддерживаются только .csv и .json")

    def _import_rows(self, rows: Iterable[Dict[str, Any]]) -> int:
        created_count = 0
        for row in rows:
            shop_name = self.shop_name or row.get("shop")
            category_name = row.get("category")
            product_name = row.get("product")

            shop, _ = Shop.objects.get_or_create(name=shop_name)
            category, _ = Category.objects.get_or_create(name=category_name)
            category.shops.add(shop)
            product, _ = Product.objects.get_or_create(name=product_name,
                                                       category=category)

            info, created = ProductInfo.objects.get_or_create(
                shop=shop, sku=row.get("sku"),
                defaults={
                    "product": product,
                    "price": int(row.get("price", 0)),
                    "price_rrc": int(
                        row.get("price_rrc", row.get("price", 0))),
                    "quantity": int(row.get("quantity", 0)),
                }
            )
            if not created:
                info.product = product
                info.price = int(row.get("price", info.price))
                info.price_rrc = int(row.get("price_rrc", info.price_rrc))
                info.quantity = int(row.get("quantity", info.quantity))
                info.save()

            params = row.get("params") or row.get("parameters") or {{}}
            if isinstance(params, str):
                try:
                    params = json.loads(params)
                except Exception:
                    params = {{}}
            for pname, pvalue in params.items():
                param, _ = Parameter.objects.get_or_create(name=pname)
                ProductParameter.objects.update_or_create(
                    product_info=info, parameter=param,
                    defaults={{"value": str(pvalue)}}
                )

            created_count += 1
        return created_count
