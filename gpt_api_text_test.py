import base64
from openai import OpenAI
import ast
import json
client = OpenAI(
    api_key="OPEN_AI_KEY", # OPENAI API 키
)

# 1. 사용자 일기 입력
user_diaries = [
    "오늘은 친구랑 카페에 갔다. 맛있는 커피를 마셨다.",
    "요즘 날씨가 자주 흐려서 기분이 가라앉는다.",
    "일이 많아서 스트레스를 받았지만 운동하고 나니 조금 나아졌다."
]

# 2. 프롬프트 생성 (3개의 일기를 모두 포함하고, 서로의 맥락을 고려해 각각 개선 요청)
prompt = f"""
다음은 사용자가 작성한 3개의 일기야. 이 일기들은 서로 같은 날에 작성된 것으로, 서로의 맥락을 고려해서 각각의 일기를 더 풍부하고 자연스럽게 개선해줘. 
그리고 개선된 일기 3개를 반드시 JSON 형식의 문자열로 반환해줘. 
예시: 
```
[
    "개선된 일기 1",
    "개선된 일기 2",
    "개선된 일기 3"   
]
```

일기1: "{user_diaries[0]}"
일기2: "{user_diaries[1]}"
일기3: "{user_diaries[2]}"

각 일기를 전체 맥락을 고려해서 자연스럽게 개선한 후, 다음과 같은 형태로 반환해줘:
[
    "개선된 일기1",
    "개선된 일기2",
    "개선된 일기3"
]
너의 output은 리스트로 파싱할 예정이기 때무에, 꼭 앞선 형식대로만 반환해줘야해.
"""
# 3. OpenAI API 호출

completion = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "user", "content": prompt}
    ]
)
# 4. 결과 출력
response = completion.choices[0].message.content.strip()
print("개선된 일기:")
print(response)
# 5. JSON 형식으로 파싱
# 코드 블록 마커 제거
cleaned_output = response.replace("```json", "").replace("```", "").strip()

# JSON 파싱
try:
    diary_list = json.loads(cleaned_output)
    for i in range(len(diary_list)):
        print(f"개선된 일기: {diary_list[i]}")
    
    # for i, diary in enumerate(diary_list, 1):
    #     print(f"{i}. {diary}")
except json.JSONDecodeError as e:
    print("JSON 파싱 실패:", e)
    print("GPT 응답 내용:\n", cleaned_output)