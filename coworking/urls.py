from django.urls import path
from . import views

app_name = 'coworking'

urlpatterns = [
    # Коворкинги
    path('', views.coworking_list, name='coworking_list'),
    path('coworking/<int:pk>/', views.coworking_detail, name='coworking_detail'),
    path('coworking/create/', views.coworking_create, name='coworking_create'),
    path('coworking/<int:pk>/edit/', views.coworking_update, name='coworking_update'),
    path('coworking/<int:pk>/delete/', views.coworking_delete, name='coworking_delete'),
    path('coworking/<int:coworking_id>/image/add/', views.coworking_image_add, name='coworking_image_add'),
    path('coworking/image/<int:pk>/delete/', views.coworking_image_delete, name='coworking_image_delete'),
    path('coworking/<int:coworking_id>/review/add/', views.review_create, name='review_create'),



    # Рабочие места
    path('workplace/<int:pk>/', views.workplace_detail, name='workplace_detail'),
    path('coworking/<int:coworking_id>/workplace/create/', views.workplace_create, name='workplace_create'),
    path('workplace/<int:pk>/edit/', views.workplace_update, name='workplace_update'),
    path('workplace/<int:pk>/delete/', views.workplace_delete, name='workplace_delete'),
    path('workplace/<int:workplace_id>/image/add/', views.workplace_image_add, name='workplace_image_add'),
    path('workplace/image/<int:pk>/delete/', views.workplace_image_delete, name='workplace_image_delete'),
    path('workplace/<int:pk>/favorite/add/', views.favorite_add, name='favorite_add'),
    path('workplace/<int:pk>/favorite/remove/', views.favorite_remove, name='favorite_remove'),


    # Бронирования
    path('bookings/', views.booking_list, name='booking_list'),
    path('bookings/create/<int:workplace_id>/', views.booking_create, name='booking_create'),
    path('bookings/<int:pk>/edit/', views.booking_update, name='booking_update'),
    path('bookings/<int:pk>/cancel/', views.booking_cancel, name='booking_cancel'),
    path('bookings/<int:booking_id>/payment/', views.booking_payment, name='booking_payment'),

    path('favorites/', views.favorite_list, name='favorite_list'),
]
