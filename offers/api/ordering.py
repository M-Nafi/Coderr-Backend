from django.db.models import QuerySet


class OrderingHelperOffers:
    @staticmethod
    def apply_ordering(queryset: QuerySet, ordering: str) -> QuerySet:
        ordering_map = {
        "-created_at": "-created_at",
        "created_at": "created_at",
        "min_price": "min_price",
        "-min_price": "-min_price",
        "-updated_at": "updated_at",  
        "updated_at": "-updated_at",    
        }
        ordering_field = ordering_map.get(ordering, "-updated_at")  
        return queryset.order_by(ordering_field)