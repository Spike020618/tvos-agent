from client import DeepSeekClient, Agent
from client import Result

task = '做一道青椒肉丝'
task_agent = Agent(name="Task Agent", instructions="分解任务为详细步骤",)

# 传递
def talk_to_task():
   print("Hello, task!")
   return Result(
       value="Done",
       agent=task_agent,
       context_variables={"module": "task"}
   )

agent = Agent(name='agent', functions=[talk_to_task])

client = DeepSeekClient()
response = client.run(
   agent=agent,
   messages=[{"role": "user", "content": "Send to task"}],
   context_variables={"username": "Spike"}
)
print(response.agent.name)
print(response.context_variables)


response = client.run(
   agent=response.agent,
   messages=[{"role": "user", "content": task}],
   context_variables={"username": "Spike"}
)
print(response.agent.name)
print(response.context_variables)
print(response.messages[0]['content'])
