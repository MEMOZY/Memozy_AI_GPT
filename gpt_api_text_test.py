import base64
from openai import OpenAI

client = OpenAI(
    api_key="OPEN_AI_KEY",
)





prompt="너는 해적이야. 해적의 말투로 말해줘"
questions="현재 너가 알기에 가장 최신의 날짜가 언젠지 내게 알려줘"
completion = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        { "role": "assistant", "content": "안녕하세요. 저는 3줄 일기를 작성해주는 시스템입니다." },
        { "role": "user","content": "나는 오늘 산에 갔다 왔어" },
        { "role": "assistant", "content": "그렇군요! 오늘 등산했군요!" },
        { "role": "user","content": "맞아. 이제 일기를 작성해줘" },
    ],
)

print(completion.choices[0].message.content)