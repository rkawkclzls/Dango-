class CustomMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 뷰가 호출되기 전에 실행될 코드

        response = self.get_response(request)

        # 뷰가 호출된 후에 실행될 코드

        return response