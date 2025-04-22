from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime


from .service import Service, Task
from .utils import get_ip

service = Service()
task = Task()

#@ensure_csrf_cookie  # 强制返回 CSRF Cookie
def index(request):
    return HttpResponse("Hello Django!")

#@ensure_csrf_cookie  # 强制返回 CSRF Cookie
def movie_search(request):
    if request.method == 'GET':
        try:
            msg = request.GET.get('message', '')
            if task.sensitiveFilter.contains_sensitive(msg):
                return JsonResponse({
                    "chat": "⚠️ 检测到敏感词",
                    "movies": "",
                    "movies_info": "",
                    "status": "error"
                })
            steps = task.planner.plan(message=msg)
            print(steps)
            chat, movies, movies_info = service.run(message=msg, steps=steps)
            return JsonResponse({
                "chat": chat,
                "movies": movies,
                "movies_info": movies_info,
                "status": "success"
            })
        except Exception as e:
            return JsonResponse({
                "chat": str(e),
                "movies": "",
                "movies_info": "",
                "status": "error"
            }, status=500)
    return JsonResponse({
        "chat": "请使用GET方法",
        "movies": "",
        "movies_info": "",
        "status": "error"
    })


def get_server_ip(request):
    return JsonResponse({'ip': get_ip()})

def show_uploader_page(request):
    return render(request, 'agent/uploader.html', {'local_ip': get_ip()})

@csrf_exempt
def handle_upload(request):
    if request.method == 'POST':
        try:
            # 处理文本输入
            text_input = request.POST.get('text', '')
            
            # 处理图片上传
            image_file = request.FILES.get('image')
            image_path = None
            if image_file:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                image_path = f'media/uploads/{timestamp}_{image_file.name}'
                with open(image_path, 'wb+') as destination:
                    for chunk in image_file.chunks():
                        destination.write(chunk)
            
            # 处理语音转文字
            audio_file = request.FILES.get('audio')
            audio_text = ""
            if audio_file:
                # 这里添加你的语音识别逻辑
                # 可以使用第三方API如百度语音识别、Azure Speech等
                audio_text = "[语音识别结果]"
            
            # 这里添加你的业务逻辑处理
            
            return JsonResponse({
                'status': 'success',
                'text': text_input,
                'image_path': image_path,
                'audio_text': audio_text
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})
