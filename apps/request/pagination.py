# in projects/pagination.py (NEW FILE or ADD TO)

from rest_framework.pagination import PageNumberPagination

class StandardResultsSetPagination(PageNumberPagination):
    """
    A standard pagination class for the API.
    Enables ?page=X and ?page_size=Y query parameters.
    """
    page_size = 25
    page_size_query_param = 'page_size'
    max_page_size = 100