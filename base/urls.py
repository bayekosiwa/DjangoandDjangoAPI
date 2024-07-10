from django.urls import path
from . import views

urlpatterns = [

    path('', views.home, name="home"),
    path('login/', views.loginPage, name="login"),
    path('register/', views.register, name="register"),
    path('logout/', views.logoutPage, name="logout"),
    path('profile/<str:pk>', views.profile, name="profile"),
    path('edit_profile/<str:pk>', views.editProfile, name="edit_profile"),
    path('room/<str:pk>', views.room, name="room"),
    path('create_room', views.createRoom, name="create_room"),
    path('edit_room/<str:pk>', views.editRoom, name="edit_room"),
    path('delete_room/<str:pk>', views.deleteRoom, name="delete_room" ),
    path('delete_message/<str:pk>', views.deleteMessage, name="delete_message"),
    path('topics', views.topics, name="topics"),
    path('activity', views.activity, name="activity")
]