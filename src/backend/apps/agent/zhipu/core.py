import base64
import json
from zhipuai import ZhipuAI

class ZhiPuClient:
    def __init__(self, key='f1677ec1cb784f3fbda4b8767bcc3c1e.PaYoK8zqumX6QFtT'):
        self.client = ZhipuAI(api_key=key)

    def chat(self, img_path, text):
        with open(img_path, 'rb') as img_file:
            img_base64 = base64.b64encode(img_file.read()).decode('utf-8')

        response = self.client.chat.completions.create(
            model="glm-4v-plus-0111",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": img_base64}},
                        {"type": "text", "text": text}
                    ]
                }
            ],
            temperature=0.1  # 降低随机性，确保稳定输出
        )

        # 解析并验证模型响应
        try:
            content = json.loads(response.choices[0].message.content)
            # 检查字段是否存在且类型正确
            if isinstance(content, dict) and "safe" in content and "response" in content:
                return bool(content["safe"]), str(content["response"])
            else:
                raise ValueError("返回的JSON缺少必要字段")
        except (json.JSONDecodeError, ValueError, KeyError, AttributeError) as e:
            print(f"解析模型响应失败: {e}")
            return {"safe": False, "response": ""}