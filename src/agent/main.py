from client import DeepSeekClient, Agent
import json

def stream_print(stream):
    messages = []
    for chunk in stream:
        #print(f"\nReceived chunk: {chunk}")
        if "delim" in chunk:
            if chunk["delim"] == "start":
                print("\n----Response started")
            elif chunk["delim"] == "end":
                print("\n----Response ended")
        elif "response" in chunk:
            response = chunk["response"]
            print("----Final Response")
            messages.extend(response.messages) # Add this line
            #print(messages)
        else:
            if chunk['content'] is not None:
                 print(chunk['content'], end='')
    return messages

client = DeepSeekClient()

def transfer_to_agent_b():
    return agent_b


agent_a = Agent(
    name="Agent A",
    instructions="你是一个乐于助人的代理。",
    functions=[transfer_to_agent_b],
)

agent_b = Agent(
    name="Agent B",
    instructions="只说中文。",
)

def get_weather(location) -> str:
    return "{'temp':67, 'unit':'F'}"

agent_c = Agent(
    name="Agent C",
    instructions="You are a helpful agent.",
    functions=[get_weather], # 自定义的调用外部函数的API，返回结构化数据
)

'''response = client.run(
    agent=agent_a,
    messages=[{"role": "user", "content": "I want to talk to agent B."}],
)

print(response.messages[-1]["content"])

stream = client.run_stream(
    agent=agent_a,
    messages=[{"role": "user", "content": "I want to talk to agent B."}],
)'''


'''
# 初始化对话历史
conversation_history = []

# 第一次对话
message = {"role": "user", "content": "你好，请介绍一下你自己。"}
stream = client.run_stream(
    agent=agent_a,
    messages=conversation_history + [message],
)
# 一般来说responses里只有一个元素
responses = stream_print(stream)
conversation_history.extend([message])
conversation_history.extend(responses)

# 第二次对话
message = {"role": "user", "content": "请推荐一些音乐。"}
stream = client.run_stream(
    agent=agent_a,
    messages=conversation_history + [message],
)
responses = stream_print(stream)
conversation_history.extend([message])
conversation_history.extend(responses)

# 第三次对话
message = {"role": "user", "content": "针对你上面推荐的音乐，请给出解析。"}
stream = client.run_stream(
    agent=agent_a,
    messages=conversation_history + [message],
)
responses = stream_print(stream)
conversation_history.extend([message])
conversation_history.extend(responses)
'''


messages = []
messages.append({"role": "user", "content": "请推荐一些摇滚音乐。"})
stream = client.run(
    agent=agent_a,
    stream=True,
    messages=messages,
)
responses = stream_print(stream)
messages.extend(responses)

print('-----------------------------------------------\n\n\n\n\n\n')
messages.append({"role": "user", "content": "针对你上面推荐的音乐，请给出解析。"})
messages.append({"role": "user", "content": "请再推荐古典音乐。"})
stream = client.run(
    agent=agent_b,
    stream=True,
    messages=messages,
)
responses = stream_print(stream)
messages.extend(responses)
