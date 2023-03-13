from django.urls import path, include
from . import views

# from . import views_fronts
app_name = 'web_grade'


urlpatterns = [
    path("", views.index, name="index"),
    path("delete_table/<str:grade_table_id>",
         views.delete_table_view, name="delete_table"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("manage_grade/", views.manage_grade_view, name="manage_grade"),
    path("grade/", views.grade_view, name="grade"),
    path("courese_list/", views.courese_list, name="courese_list"),
    path("show_grade/<str:grade_table_id>",
         views.show_grade_view, name="show_grade"),
    path("change_status/<str:grade_table_id>",
         views.change_status_view, name="change_status"),
    path("course_info/<str:grade_table_id>",
         views.course_info, name="course_info"),
     path("search_subject/", views.search_subject_view, name="search_subject"),

]
