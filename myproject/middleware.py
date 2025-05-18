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
    
class ContentSecurityPolicyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Генерация nonce
        nonce = base64.b64encode(os.urandom(16)).decode('utf-8')
        request.csp_nonce = nonce

        response = self.get_response(request)

        # CSP заголовок
        response['Content-Security-Policy'] = (
            f"default-src 'none'; "
            f"script-src 'self' 'nonce-{nonce}'; "
            f"style-src 'self'; "
            f"img-src 'self'; "
            f"connect-src 'self'; "
            f"font-src 'self';"
        )
        return response