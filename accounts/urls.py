from django.urls import path
from django.urls.conf import re_path
# from .views import login_view, logout_view, register_user, email_verify, verify_phone, phonecodeverify, change_pass, forgot_pass, forgot_change_pass, profile_view, resend_email, delete_profile
from .views import login_view, logout_view, register_prop, register_user, google_login

# from shop.views import shop_registeration_view
# from manufacturer.views import manufacturer_registeration_view
# from service.views import service_registeration_view

urlpatterns = [
    path('login/',  login_view, name='login'),
    path('register/',  register_user, name='register'),
    path('register/p/',  register_prop, name='registerprop'),
    path('logout/', logout_view, name='logout'),
    re_path(r'^google-login/$', google_login, name="google_login"),


]


