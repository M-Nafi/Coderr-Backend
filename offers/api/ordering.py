from django.db.models import QuerySet


class OrderingHelperOffers:
    @staticmethod
    def apply_ordering(queryset: QuerySet, ordering: str) -> QuerySet:
        """
        Applies ordering to a queryset of offers.
        
        :param queryset: A QuerySet of offers.
        :param ordering: A string indicating how to order the queryset.
            Supported values are:
            - created_at: Orders by creation time in ascending order.
            - -created_at: Orders by creation time in descending order.
            - min_price: Orders by minimum price in ascending order.
            - -min_price: Orders by minimum price in descending order.
            - updated_at: Orders by last update time in ascending order.
            - -updated_at: Orders by last update time in descending order.
            If not specified, defaults to -updated_at.
        :return: A QuerySet ordered according to the specified ordering.
        """
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