class XForwardedForMiddleware:
    """
    Мидлварь определяет реальный IP-адрес клиента,
    когда приложение работает за прокси-сервером Nginx
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if "HTTP_X_FORWARDED_FOR" in request.META:
            ip = request.META["HTTP_X_FORWARDED_FOR"].split(",")[0].strip()
            request.META["REMOTE_ADDR"] = ip
        elif "HTTP_X_REAL_IP" in request.META:
            request.META["REMOTE_ADDR"] = request.META["HTTP_X_REAL_IP"]
        return self.get_response(request)
