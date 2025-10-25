from django.urls import path
from . import views

urlpatterns = [
    path('bubbles/', views.get_bubble_data, name='get_bubble_data'),
]