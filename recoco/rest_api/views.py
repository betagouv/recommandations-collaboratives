from rest_framework_simplejwt.views import (
    TokenObtainPairView as BaseTokenObtainPairView,
    TokenRefreshView as BaseTokenRefreshView,
)


class TokenObtainView(BaseTokenObtainPairView):
    pass


class TokenRefreshView(BaseTokenRefreshView):
    pass
