class ApiTrailingSlashMiddleware:
    """Resolve slashless API paths without redirecting the original request."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path_info.startswith('/api/') and not request.path_info.endswith('/'):
            request.path_info += '/'
            request.META['PATH_INFO'] = request.path_info
        return self.get_response(request)