import time

from django.utils.deprecation import MiddlewareMixin

import logging


class RequestLoggingMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger('apps.requests')

    def process_request(self, request):
        request.start_time = time.time()

    def process_response(self, request, response):
        duration = time.time() - getattr(request, 'start_time', time.time())

        self.logger.info(
            f'{request.method} {request.path} {response.status_code}',
            extra={
                'method': request.method,
                'path': request.path,
                'status_code': response.status_code,
                'duration': duration,
                'user_id': getattr(request.user, 'id', None),
                'ip_address': self.get_client_ip(request)
            }
        )
        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
