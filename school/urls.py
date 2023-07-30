from django.urls import path
from django.contrib.auth import views as auth_views
from . import views


app_name ='school'

urlpatterns = [
  
    path("login/", views.MyLoginView.as_view(), name="login"),
    path('logout/', auth_views.LogoutView.as_view(next_page='/login'), name='logout'),
    path('user/detail/', views.CustomerUserDetailView.as_view(), name='user_detail'),
    path('user/update/', views.CustomerUserUpdateView.as_view(), name='user_update'),
    path('student/<int:student_pk>/enrolled-packages/', views.EnrolledPackageListView.as_view(), name='enrolled_package_list'),
    path('student/<uuid:enrolled_package_id>/sessions/', views.SessionListView.as_view(), name='session_list'),
    path('user/change_password/', views.ChangePasswordView.as_view(), name='change_password'),
    path('user/inicio/',views.CreateMessageView.as_view(),name="inicio"),
    path('',views.Index.as_view(),name="index")
]