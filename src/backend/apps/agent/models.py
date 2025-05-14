from django.db import models

# Create your models here.
from django.contrib.auth.models import User

class UserHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='history_records')
    action = models.CharField(max_length=255, help_text="用户执行的操作描述")
    timestamp = models.DateTimeField(auto_now_add=True, help_text="操作时间")
    ip_address = models.GenericIPAddressField(null=True, blank=True, help_text="用户操作的IP地址")
    user_agent = models.TextField(null=True, blank=True, help_text="浏览器或客户端信息")
    extra_data = models.JSONField(null=True, blank=True, help_text="附加信息，例如参数、状态等")

    class Meta:
        verbose_name = "用户历史记录"
        verbose_name_plural = "用户历史记录"
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user.username} - {self.action} at {self.timestamp}"