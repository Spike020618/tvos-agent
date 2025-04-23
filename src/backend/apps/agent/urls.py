from django.urls import path, re_path
from django.views.static import serve
from django.conf import settings
from . import views

# 配置url地址和view视图的映射关系
urlpatterns = [
    path("", views.index, name="index"),

    # 核心业务api
    path("search", views.search, name='search'),
    path('media/<int:media_id>', views.stream_media, name='media-stream'),

    # 工具api
    path('uploader_page', views.show_uploader_page, name='uploader page'),
    path('uploader', views.handle_upload, name='handle uploader'),
    path('server_ip', views.get_server_ip),
]