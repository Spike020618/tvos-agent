from django.urls import path

from . import views

# 配置url地址和view视图的映射关系
urlpatterns = [
    path("", views.index, name="index"),

    path("media_search", views.media_search, name='media search'),
    path("voice_media_search", views.voice_media_search, name='voice media search'),
    path('media/<int:media_id>', views.stream_media, name='media-stream'),
    path('server_ip', views.get_server_ip),
    path('see', views.see, name='see'),

    # 手机端api
    path('uploader_page', views.show_uploader_page, name='uploader page'),
    path('upload', views.upload, name='upload'),
]