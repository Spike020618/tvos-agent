import base64
from zhipuai import ZhipuAI

img_path = "background.png"
with open(img_path, 'rb') as img_file:
    img_base = base64.b64encode(img_file.read()).decode('utf-8')

client = ZhipuAI(api_key="f1677ec1cb784f3fbda4b8767bcc3c1e.PaYoK8zqumX6QFtT") # 填写您自己的APIKey
response = client.chat.completions.create(
    model="glm-4v-plus-0111",  # 填写需要调用的模型名称
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
            "text": "这个图片和什么影视作品相关呢？"
          }
        ]
      }
    ]
)
print(response.choices[0].message)