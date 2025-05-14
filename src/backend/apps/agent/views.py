from django.http import HttpResponse, JsonResponse, StreamingHttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from datetime import datetime
import os
import re
import json


from .service import Service, Task, SseView
from .utils import get_ip

service = Service()
task = Task()

#@ensure_csrf_cookie  # 强制返回 CSRF Cookie
def index(request):
    return HttpResponse("Hello Django!")

def media_search(request):
    if request.method == 'GET':
        try:
            msg = request.GET.get('message', '')
            if task.sensitiveFilter.contains_sensitive(msg):
                return JsonResponse({
                    "chat": "⚠️ 检测到敏感词",
                    "medias": "",
                    "medias_info": "",
                    "status": "error"
                })
            medias, medias_info = service.media_search(message=msg)
            return JsonResponse({
                "chat": "",
                "medias": medias,
                "medias_info": medias_info,
                "status": "success"
            })
        except Exception as e:
            return JsonResponse({
                "chat": str(e),
                "medias": "",
                "medias_info": "",
                "status": "error"
            }, status=500)
    return JsonResponse({
        "chat": "请使用GET方法",
        "medias": "",
        "medias_info": "",
        "status": "error"
    })

def voice_media_search(request):
    if request.method == 'GET':
        try:
            msg = request.GET.get('message', '')
            if task.sensitiveFilter.contains_sensitive(msg):
                return JsonResponse({
                    "chat": "⚠️ 检测到敏感词",
                    "medias": "",
                    "medias_info": "",
                    "status": "error"
                })
            steps = task.planner.plan(message=msg)
            print(steps)
            chat, medias, medias_info = service.voice_media_search(message=msg, steps=steps)
            return JsonResponse({
                "chat": chat,
                "medias": medias,
                "medias_info": medias_info,
                "status": "success"
            })
        except Exception as e:
            return JsonResponse({
                "chat": str(e),
                "medias": "",
                "medias_info": "",
                "status": "error"
            }, status=500)
    return JsonResponse({
        "chat": "请使用GET方法",
        "medias": "",
        "medias_info": "",
        "status": "error"
    })

def stream_media(request, media_id):
    # 1. 获取视频文件名（安全处理）
    # 安全校验文件名
    media_path = service.get_media_path(media_id)
    if media_path == '':
        return HttpResponseBadRequest("media not found")

    # 3. 获取文件大小
    file_size = os.path.getsize(media_path)
    range_header = request.headers.get('Range', '')

    # 4. 处理范围请求（断点续传）
    if range_header:
        match = re.search(r'bytes=(\d+)-(\d+)?', range_header)
        if not match:
            return HttpResponseBadRequest("Invalid Range header")

        first_byte = int(match.group(1))
        last_byte = int(match.group(2)) if match.group(2) else file_size - 1
        chunk_size = last_byte - first_byte + 1

        def chunk_generator():
            with open(media_path, 'rb') as f:
                f.seek(first_byte)
                remaining = chunk_size
                while remaining > 0:
                    read_size = min(4096, remaining)  # 4KB分块
                    chunk = f.read(read_size)
                    if not chunk:
                        break
                    remaining -= len(chunk)
                    yield chunk

        response = StreamingHttpResponse(
            chunk_generator(),
            status=206,
            content_type='video/mp4'
        )
        response['Content-Range'] = f'bytes {first_byte}-{last_byte}/{file_size}'
        response['Content-Length'] = str(chunk_size)
    else:
        # 5. 完整文件传输（小文件备用方案）
        response = StreamingHttpResponse(
            open(media_path, 'rb'),
            content_type='video/mp4'
        )
        response['Content-Length'] = str(file_size)

    # 6. 设置关键响应头
    response['Accept-Ranges'] = 'bytes'
    response['Content-Disposition'] = f'inline; filename="{os.path.basename(media_path)}"'
    return response

@csrf_exempt
def see(request):
    sse_view = SseView()  # 每个连接新建实例
    response = StreamingHttpResponse(sse_view.event_stream(), content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    return response

def get_server_ip(request):
    return JsonResponse({'ip': get_ip()})

def show_uploader_page(request):
    return render(request, 'agent/uploader.html', {'local_ip': get_ip()})

@csrf_exempt
def upload(request):
    if request.method == 'POST':
        try:
            # 处理文本输入
            text_input = request.POST.get('text', '')

            # 处理图片上传
            image_file = request.FILES.get('image')
            image_path = None
            if image_file:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                image_path = f'image/{timestamp}_{image_file.name}'
                with open(image_path, 'wb+') as destination:
                    for chunk in image_file.chunks():
                        destination.write(chunk)

            # 分析结果
            safe, medias, medias_info = service.image_analyze(image_path, text_input)
            print(safe, medias, medias_info)
            if safe:
                return JsonResponse({
                    'status': 'success',
                    'message': '解析成功！'
                })
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': '图片涉及敏感信息！'
                })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})