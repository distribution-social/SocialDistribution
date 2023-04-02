from django.urls import is_valid_path
from django.shortcuts import redirect

class RemoveTrailingSlashMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if the path is valid and does not end with a trailing slash
        if not is_valid_path(request.path_info) and request.path_info.endswith('/'):
            # Add a trailing slash to the path
            new_url = request.path_info[:-1]

            query_params = request.GET.urlencode()
            if query_params:
                new_url += '?' + query_params

            # Redirect to the new URL
            return redirect(new_url, permanent=True)

        response = self.get_response(request)
        return response