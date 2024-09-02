from django.urls import path
from .views import LoginWithGoogle
from .userviews import get_user_details,add_user_details

urlpatterns = [
    path('login-with-google/', LoginWithGoogle.as_view(),name=('login-with-google')),
    path('add-user/', add_user_details, name='add_user_details'),
    path('get-users/', get_user_details, name='get_user_details'),
]