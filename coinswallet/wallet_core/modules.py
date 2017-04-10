from coinswallet.settings import MAX_GET_RESPONSE_PER_PAGE
from django.core.paginator import Paginator, EmptyPage

__author__ = 'kaushal'


class GetRequestPaginator(object):
    """
    Used to paginate queryset:
    i.e. breaking large number of items in queryset in pages of smaller subset
    """
    def __init__(self, queryset, page_requested, page_size):
        # original queryset
        self.queryset = queryset

        # current requested page
        self.curr_page = 1 if page_requested < 1 else page_requested

        # page size
        self.page_size = page_size if page_size < MAX_GET_RESPONSE_PER_PAGE \
            else MAX_GET_RESPONSE_PER_PAGE

        self.total_count = None
        self.next_page = None
        self.previous_page = None
        self.sub_queryset = None

    def paginate(self):
        """
        calculate sub-queryset from original queryset,
        returns new queryset (sub-queryset), and also content's meta-data
        meta-data: information relevant to API client for subsequent request
        meta-data consists of:
        - total_count: total number of items in queryset
        - next_page: next page number for fetching next set of data
        - prev_page: similarly, previous set of data
        """
        # Get total number of items in original query
        self.total_count = self.queryset.count()

        # Paginate queryset, create new subset of original queryset
        paginator = Paginator(self.queryset, self.page_size)
        try:
            self.sub_queryset = paginator.page(self.curr_page)

            if self.sub_queryset.has_next():
                self.next_page = self.curr_page + 1
            else:
                self.next_page = self.curr_page

        except EmptyPage:
            # If page is out of range, deliver last page of results.
            self.sub_queryset = paginator.page(paginator.num_pages)
            self.next_page = paginator.num_pages

        # calculate previous page for meta data
        self.previous_page = self.next_page - 2
        if self.previous_page < 1:
            self.previous_page = 1

        # return new query set and meta data for page info
        meta_data = {
            'total_count': self.total_count,
            'next_page': self.next_page,
            'previous_page': self.previous_page
        }
        return self.sub_queryset, meta_data
