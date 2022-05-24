#for pagination
from django.conf import settings
from rest_framework import pagination
from rest_framework.response import Response

class CustomPagination(pagination.PageNumberPagination):
    page_size = 15
    page_size_query_param = 'size'
    max_page_size = 10000

    def get_paginated_response(self, data):
        # print("self ", data)
        # print(self.request)
        current_page=self.request.GET.get("page", "1") #TODO: fix the page issue
        if current_page.isdigit():
            current_page=int(current_page)
        else: current_page=1

        total_pages=self.page.paginator.num_pages
        absolute_url=self.request.build_absolute_uri(self.request.path)
        params = self.request.GET.copy()
        if "page" in params:
            del params["page"]
        # print(params)
        current_url="{}?{}".format(absolute_url, params.urlencode())
        def pick_n_pages(pages, n=3, first=True):
            size=len(pages)
            links=[]; _pages=[]
            if n>size:
                _pages= pages
            else: #more elements(size) than the required list to be returned
                if first:
                    _pages=pages[:n]
                else:#[1,2,3,4,5] 1
                    index=size-n
                    first_pages=pages[index:]
                    _pages=pages-first_pages
            
            #generate links here
            for _page in _pages:
                # print(params)
                _params=params
                if "page" in _params: #sometime the page parameter is repeated
                    del _params["page"]
                _params.update({"page": _page})
                url="{}?{}".format(absolute_url, _params.urlencode())
                links.append({"index":_page, "url":url})
            return links
            
        last_pages=pick_n_pages([i for i in range(current_page, total_pages, 1)])
        first_pages=pick_n_pages([i for i in range(1, current_page, 1)])

        is_paginated=self.page.has_next() or self.page.has_previous()
        last_index=self.page.end_index()
        params.update({"page": last_index})
        last_url={"index":last_index, "url":"{}?{}".format(absolute_url, params.urlencode())} if is_paginated else None
        
        return Response({
            "is_paginated": is_paginated,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'last_pages':last_pages,
            'first_pages':first_pages,
            'count': self.page.paginator.count,
            'total_pages': total_pages,
            'results': data,
            'absolute_url':absolute_url,
            'current_url':current_url,
            # 'last_url':last_url
        })