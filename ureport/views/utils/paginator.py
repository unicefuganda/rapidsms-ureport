from django.core.paginator import Paginator, QuerySetPaginator, Page, InvalidPage
import math
from django.db import connection
from django.db.utils import DatabaseError
from ureport.models import UreportContact


class UreportPaginator(Paginator):
    """
    Overrides the count method to get an estimate instead of actual count when not filtered
    also use better  pagination with large datasets :)

    {# with: page = ureport_paginator.page(1) #}
    {% for num in page.leading_range %} ...
    {% for num in page.main_range %} ...
    {% for num in page.trailing_range %} ...

    Additionally, ``page_range`` contains a nun-numeric ``False`` element
    for every transition between two ranges.

    {% for num in page.page_range %}
        {% if not num %} ...  {# literally output dots #}
        {% else %}{{ num }}
        {% endif %}
    {% endfor %}

    Additional arguments passed to the constructor allow customization of
    how those bocks are constructed:

    body=5, tail=2

    [1] 2 3 4 5 ... 91 92
    |_________|     |___|
    body            tail
              |_____|
              margin

    body=5, tail=2, padding=2

    1 2 ... 6 7 [8] 9 10 ... 91 92
            |_|     |__|
             ^padding^
    |_|     |__________|     |___|
    tail    body             tail

    ``margin`` is the minimum number of pages required between two ranges; if
    there are less, they are combined into one.

    When ``align_left`` is set to ``True``, the paginator operates in a
    special mode that always skips the right tail, e.g. does not display the
    end block unless necessary. This is useful for situations in which the
    exact number of items/pages is not actually known.
    credit:

    http://djangosnippets.org/snippets/773/
    """

    def __init__(self, *args, **kwargs):
        self.body = kwargs.pop('body', 10)
        self.tail = kwargs.pop('tail', 2)
        self.align_left = kwargs.pop('align_left', False)
        self.margin = kwargs.pop('margin', 4)  # TODO: make the default relative to body?
        # validate padding value
        max_padding = int(math.ceil(self.body / 2.0) - 1)
        self.padding = kwargs.pop('padding', min(4, max_padding))
        if self.padding > max_padding:
            raise ValueError('padding too large for body (max %d)' % max_padding)
        super(UreportPaginator, self).__init__(*args, **kwargs)

    def page(self, number, *args, **kwargs):
        """Return a standard ``Page`` instance with custom, digg-specific
        page ranges attached.
        """

        try:
            page = super(UreportPaginator, self).page(number, *args, **kwargs)
            number = int(number) # we know this will work
        except InvalidPage, e:
            page = super(UreportPaginator, self).page(1, *args, **kwargs)
            number = 1





        # easier access
        num_pages, body, tail, padding, margin = \
            self.num_pages, self.body, self.tail, self.padding, self.margin

        # put active page in middle of main range
        main_range = map(int, [
            math.floor(number - body / 2.0) + 1, # +1 = shift odd body to right
            math.floor(number + body / 2.0)])
        # adjust bounds
        if main_range[0] < 1:
            main_range = map(abs(main_range[0] - 1).__add__, main_range)
        if main_range[1] > num_pages:
            main_range = map((num_pages - main_range[1]).__add__, main_range)

        # Determine leading and trailing ranges,
        # Example:
        #     total pages=100, page=4, body=5, (default padding=2)
        #     1 2 3 [4] 5 6 ... 99 100
        #     total pages=100, page=4, body=5, padding=1
        #     1 2 3 [4] 5 ... 99 100

        if main_range[0] <= tail + margin:
            leading = []
            main_range = [1, max(body, min(number + padding, main_range[1]))]
            main_range[0] = 1
        else:
            leading = range(1, tail + 1)
            # basically same for trailing range, but not in ``left_align`` mode
        if self.align_left:
            trailing = []
        else:
            if main_range[1] >= num_pages - (tail + margin) + 1:
                trailing = []
                if not leading:
                    main_range = [1, num_pages]
                else:
                    main_range = [min(num_pages - body + 1, max(number - padding, main_range[0])), num_pages]
            else:
                trailing = range(num_pages - tail + 1, num_pages + 1)

        # finally, normalize values that are out of bound; this basically
        # fixes all the things the above code screwed up in the simple case
        # of few enough pages where one range would suffice.
        main_range = [max(main_range[0], 1), min(main_range[1], num_pages)]

        # make the result of our calculations available as custom ranges
        # on the ``Page`` instance.
        page.main_range = range(main_range[0], main_range[1] + 1)
        page.leading_range = leading
        page.trailing_range = trailing
        page.page_range = reduce(lambda x, y: x + ((x and y) and [False]) + y,
                                 [page.leading_range, page.main_range, page.trailing_range])

        page.__class__ = CustomPage
        return page


    def _get_count(self):
        """
        Changed to use an estimate if the estimate is greater than 10,000
        Returns the total number of objects, across all pages.
        """
        if self._count is None:
            try:
                self._count = self.object_list.count()
            except (AttributeError, TypeError, DatabaseError):
                # AttributeError if object_list has no count() method.
                # TypeError if object_list.count() requires arguments
                # (i.e. is of type list).
                self._count = len(self.object_list)
        return self._count

    count = property(_get_count)


class CustomPage(Page):
    def __str__(self):
        return " ... ".join(filter(None, [
            " ".join(map(str, self.leading_range)),
            " ".join(map(str, self.main_range)),
            " ".join(map(str, self.trailing_range))]))


def ureport_paginate(objects_list, perpage, page, p):
    paginator = UreportPaginator(objects_list, perpage, body=12, padding=2)
    filtered_list = paginator.page(page).object_list

    try:
        count = objects_list.count()
    except:
        count = len(objects_list)

    return dict(total=count, count=len(filtered_list), paginator=paginator, c_page=paginator.page(page), page=page,
                object_list=filtered_list)
