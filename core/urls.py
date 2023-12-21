from django.urls import path
from .views import *
urlpatterns = [
    path('register/', register_view),

    path('profile/', get_profile),
    path('update/profile/', update_profile),
    path('update/password/', update_password),
    path('delete/user/', delete_user),

 

    path('item/create/', create_item),
    path('item/lost/', items_api_lost),
    path('get/match/<str:id>/', get_item_match),
    path('item/edit/<str:id>/', get_item),
    path('edit/item/<str:id>/', edit_item),
    path('delete/item/<str:id>/', delete_item),

    path('deny/match/<str:id>/', deny_matching),
    path('accept/match/<str:id>/', accept_matching),
    path('recieved/match/<str:id>/', recieved_item),
    path('get/notifications/', get_notifications),
    path('read/notification/<int:id>/', mark_notification_as_read),


    path('item/found/', items_api_found),




   

]
