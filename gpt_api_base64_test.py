import os
import base64
import json
from openai import OpenAI
"""
Base64로 인코딩 된 이미지 URL이 저장된 JSON 파일을 읽은 후
URL값을 gpt api에게 넘기는 코드
"""

client = OpenAI(
    api_key="OPEN_AI_KEY",
)


# JSON 파일에서 이미지 URL 읽기
json_data = "./data/img2base64.json"


# JSON 파일에서 특정 이미지 URL 읽기
image_filename = "002.jpg"
with open(json_data, "r", encoding="utf-8") as json_file:
    image_data = json.load(json_file)
    image_url = image_data.get(image_filename, "")

if image_url:
    print(f"{image_filename} URL: {image_url}")
    
    # OpenAI API 호출 코드

    
    prompt = "이 사진에 대해 설명해줘"
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    { "type": "text", "text": prompt },
                    {
                        "type": "image_url",
                        "image_url": { "url": image_url },
                    },
                ],
            }
        ],
    )
    
    print(completion.choices[0].message.content)
else:
    print(f"{image_filename} not found in the JSON file.")