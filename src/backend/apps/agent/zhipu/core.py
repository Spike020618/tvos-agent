import base64
from zhipuai import ZhipuAI

class ZhiPuClient:
    def __init__(self, key='f1677ec1cb784f3fbda4b8767bcc3c1e.PaYoK8zqumX6QFtT'):
        self.client = ZhipuAI(api_key=key)
    
    def chat(self, img_path, text):
        with open(img_path, 'rb') as img_file:
            img_base = base64.b64encode(img_file.read()).decode('utf-8')

        response = self.client.chat.completions.create(
            model="glm-4v-plus-0111",
            messages=[
            {
                "role": "user",
                "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": img_base
                    }
                },
                {
                    "type": "text",
                    "text": text
                }
                ]
            }
            ]
        )
        return response.choices[0].message.content