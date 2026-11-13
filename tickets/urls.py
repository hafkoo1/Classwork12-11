
from django.urls import path
from . import views


urlpatterns = [
    path('', views.ticket_list, name='ticket_list'),
    path('create/', views.ticket_create, name='ticket_create'),
    path('<int:ticket_id>/', views.ticket_detail, name='ticket_detail'),

    path(
        '<int:ticket_id>/action/<str:action>/',
        views.ticket_action,
        name='ticket_action'
    ),

    path(
        '<int:ticket_id>/priority/',
        views.ticket_priority,
        name='ticket_priority'
    ),

    path(
        '<int:ticket_id>/assign/',
        views.ticket_assign,
        name='ticket_assign'
    ),
]
