from rest_framework.pagination import PageNumberPagination

class PaginateHabits(PageNumberPagination):
    """По страничная пагинация привычек
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 30
