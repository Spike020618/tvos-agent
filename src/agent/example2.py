from client import DeepSeekClient, Agent
from client import Result

agent = Agent(name='agent', instructions='做影视推荐，内容从以下筛选：{"movies":[{"name":"Inception","type":"Science Fiction","duration":148,"country":"USA"},{"name":"The Grand Budapest Hotel","type":"Comedy","duration":99,"country":"USA"},{"name":"Parasite","type":"Thriller","duration":132,"country":"South Korea"},{"name":"Amélie","type":"Romance","duration":122,"country":"France"},{"name":"Spirited Away","type":"Animation","duration":125,"country":"Japan"},{"name":"霸王别姬","type":"Drama","duration":171,"country":"China"},{"name":"卧虎藏龙","type":"Action","duration":120,"country":"China"},{"name":"无间道","type":"Crime","duration":101,"country":"Hong Kong, China"},{"name":"让子弹飞","type":"Comedy","duration":132,"country":"China"},{"name":"大话西游","type":"Fantasy","duration":95,"country":"Hong Kong, China"},{"name":"红海行动","type":"Action","duration":138,"country":"China"},{"name":"流浪地球","type":"Science Fiction","duration":125,"country":"China"},{"name":"我不是药神","type":"Drama","duration":117,"country":"China"},{"name":"战狼2","type":"Action","duration":123,"country":"China"},{"name":"芳华","type":"Drama","duration":136,"country":"China"},{"name":"少年的你","type":"Drama","duration":135,"country":"China"},{"name":"哪吒之魔童降世","type":"Animation","duration":110,"country":"China"},{"name":"长津湖","type":"War","duration":176,"country":"China"},{"name":"唐人街探案","type":"Comedy","duration":135,"country":"China"},{"name":"叶问","type":"Action","duration":106,"country":"Hong Kong, China"}]}')

client = DeepSeekClient()

response = client.run(
   agent=agent,
   messages=[{"role": "user", "content": '请推荐一些中文电影'}],
   context_variables={"username": "Spike"}
)
print(response.agent.name)
print(response.context_variables)
print(response.messages[0]['content'])
