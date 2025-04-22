import requests

url = "https://api.deepseek.com"
headers = {
    'Authorization': 'd53a6d90486e462aa755d198e940ea9d'
}
files = {'image': open('background.png', 'rb')}
response = requests.post(url, headers=headers, files=files)

if response.status_code == 200:
    print("Image uploaded successfully!")
else:
    print(f"Failed to upload image: {response.text}")