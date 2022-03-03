from django.urls import path

from . import views


app_name = 'netease'
urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.login, name='login'),
    path('register', views.register, name='register'),
    path('logout', views.logout, name='logout'),
    # path('ranking', views.ranking, name='ranking'),
    # path('comment', views.comment, name='comment'),
    # path('words', views.words, name='words'),
]