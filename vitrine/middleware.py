import logging

import re

logger = logging.getLogger(__name__)


class HeartbeatLogFilter:
    def __init__(self, get_response):
        self.get_response = get_response
        self.heartbeat_pattern = re.compile(r'/heartbeat/')

    def __call__(self, request):
        response = self.get_response(request)
        
        # Silencia apenas logs de heartbeat bem-sucedidos
        if (self.heartbeat_pattern.search(request.path) and 
            response.status_code == 200):
            # Não loga no console, mas mantém no arquivo se configurado
            return response
            
        return response