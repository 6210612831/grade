from django.urls import path, include
from . import views

# from . import views_fronts
app_name = 'grade'


urlpatterns = [
    path("", views.index, name="index"),
    path("delete_table/<str:grade_table_id>",
         views.delete_table_view, name="delete_table"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("manage_grade/", views.manage_grade_view, name="manage_grade"),
    path("grade/", views.grade_view, name="grade"),
    path("courese_list/", views.courese_list, name="courese_list"),


]
