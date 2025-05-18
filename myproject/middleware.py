import base64
import os

class NoCacheMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Пример: запрещаем кэширование только для страниц с авторизацией
        if request.user.is_authenticated:
            response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
        
        return response
    
# class ContentSecurityPolicyMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response
#
#     def __call__(self, request):
#         response = self.get_response(request)
#         response['Content-Security-Policy'] = (
#             "default-src 'self'; "
#             "style-src 'self' https://fonts.googleapis.com 'unsafe-inline'; "
#             "script-src 'self' https://cdn.jsdelivr.net 'unsafe-inline'; "
#             "img-src 'self' https://storage.yandexcloud.net; "
#             "font-src https://fonts.gstatic.com;"
#         )
#         return response