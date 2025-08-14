from django.urls import path
from . import views

app_name = 'stories'

urlpatterns = [
    path('', views.home, name='home'),
    path('stories/', views.story_list, name='story_list'),
    path('story/<int:story_id>/', views.story_detail, name='story_detail'),
    path('generate/', views.generate_story_ajax, name='generate_story'),
    path('status/<str:session_id>/', views.check_generation_status, name='check_status'),
]