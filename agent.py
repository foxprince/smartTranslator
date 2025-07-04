# 导入必要的库
from strands import Agent, tool  # 导入 strands 库中的 Agent 和 tool 类
from strands.models import BedrockModel  # 导入 BedrockModel 类用于 AI 模型调用
from strands_tools import http_request  # 导入 http_request 工具函数用于发送 HTTP 请求

# 定义天气助手的系统提示词
WEATHER_SYSTEM_PROMPT = """You are a weather assistant with HTTP capabilities. You can:
1. Make HTTP requests to the National Weather Service API
2. Process and display weather forecast data
3. Provide weather information for locations in the United States

When retrieving weather information:
1. First get the coordinates or grid information using https://api.weather.gov/points/{latitude},{longitude} or https://api.weather.gov/points/{zipcode}
2. Then use the returned forecast URL to get the actual forecast

When displaying responses:
- Format weather data in a human-readable way
- Highlight important information like temperature, precipitation, and alerts
- Handle errors appropriately
- Convert technical terms to user-friendly language

Always explain the weather conditions clearly and provide context for the forecast.
Always response in Chinese"""  # 系统提示词，指导 AI 如何作为天气助手提供服务

# 定义工具函数
@tool  # 使用 @tool 装饰器定义一个工具函数
def word_count(text: str) -> int:  # 定义计算文本字数的函数
    """Count words in text."""  # 函数说明：计算文本中的单词数
    return len(text.split())  # 返回文本分割后的单词数量

# 配置 AI 模型
bedrock_model = BedrockModel(
    model_id="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
    region_name='us-west-2',
    temperature=0.3,
    profile="lumia"  # 指定 profile
)

# 创建并使用天气代理
agent = Agent(  # 创建 Agent 实例
    system_prompt=WEATHER_SYSTEM_PROMPT,  # 设置系统提示词
    tools=[word_count, http_request],  # 配置可用工具列表：字数统计和HTTP请求
    model=bedrock_model,  # 指定使用的 AI 模型
)

# 向代理发送查询请求
response = agent(  # 调用 agent 并获取响应
    "What's the weather like in Washington D.C? Also how many words are in the response?"  # 询问华盛顿特区的天气情况并统计回复字数
)