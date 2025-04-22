from django.urls import path
from . import views

# 配置url地址和view视图的映射关系
urlpatterns = [
    path("", views.index, name="index"),
    path("search", views.search, name='search'),
    path('uploader_page', views.show_uploader_page, name='uploader page'),
    path('uploader', views.handle_upload, name='handle uploader'),
    path('server_ip', views.get_server_ip)
]