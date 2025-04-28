from openai import OpenAI
import base64
import json
import os
from datetime import datetime
from io import BytesIO
from PIL import Image

client = OpenAI(
    api_key="openai_api_key",  
)

# 대화 메시지 추가 함수
def add_message(conversation_history, gpt_content, user_content):
    if user_content:
        conversation_history["user"].append(user_content)
    if gpt_content:
        conversation_history["assistant"].append(gpt_content)

# 이미지 기반 첫 코멘트 생성 함수
def generate_first_comment(encoded_image,prompt):
    messages = [
        {
            "role": "system",
            "content": f"{prompt}"
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{encoded_image}",
                        "detail": "low"
                    }
                }
            ]
        }
    ]

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages
        # temperature=0.5
    )
    # 첫 코멘트 내용 대화내역 추가
    add_message(conversation_history, response.choices[0].message.content.strip(), prompt)

    return response.choices[0].message.content.strip()

# 대화용 GPT API 호출 함수 (최대 3회 대화)
def chat_with_gpt(conversation_history, iter_num=3):
    messages = [{"role": "user", "content": conversation_history["text_prompt"]}]
    for user_msg, gpt_msg in zip(conversation_history["user"], conversation_history["assistant"]):
        messages.append({"role": "user", "content": user_msg})
        messages.append({"role": "assistant", "content": gpt_msg})

    for turn in range(iter_num):
        user_input = input("You: ")
        if user_input.strip().lower() == "end" or turn == iter_num - 1: # 사용자가 end를 입력하거나 지정 반복 수에 도달하면 대화 종료
            break

        messages.append({"role": "user", "content": user_input})

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages
        )

        gpt_response = response.choices[0].message.content.strip()
        add_message(conversation_history, gpt_response, user_input)

        print(f"GPT: {gpt_response}")

        # 대화 업데이트
        messages.append({"role": "assistant", "content": gpt_response})

    print("\n💬 대화가 종료되었습니다. 이제 일기를 생성할게요!\n")

# 이미지 + 대화 기반 GPT 일기 생성 함수
def generate_diary_with_image(conversation_history, encoded_image):
    messages = [{"role": "user", "content": conversation_history["img_prompt"]}]
    for user_msg, assistant_msg in zip(conversation_history["user"], conversation_history["assistant"]):
        messages.append({"role": "user", "content": user_msg})
        messages.append({"role": "assistant", "content": assistant_msg})

    messages.append({
        "role": "user",
        "content": [
            {"type": "text", "text": "위의 대화 내용을 참고해서 이 이미지에 대한 일기를 작성해줘."},
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{encoded_image}",
                    "detail": "high"
                }
            }
        ]
    })

    response = client.chat.completions.create(
        model="ft:gpt-4o-2024-08-06:personal:capstone150img:BMxNfNjK",
        messages=messages
        # temperature=0.7
    )

    return response.choices[0].message.content.strip()

# 초기 프롬프트
first_comment_prompt="너는 사용자의 사진일기에 대해 먼저 사진을 보고 추측하여 사용자로부터 대화를 유도하는 역할이야. 이미지를 보고 '~~한 것같은 사진이네요. 이 사진에 대해 알려주세요!' 라는 식으로 말해."
text_prompt = "내가 너에게 사진에 대한 정보를 알려줄거야. 너는 잘 듣고 이후 일기 작성할 때 활용해줘. 추가 궁금한 게 있으면 질문해도 좋아. 대화는 이전 내용을 참고해서 자연스럽게 이어가."
img_prompt = "너는 나의 그림일기를 대신 작성해주는 역할이야. 내가 너에게 사진을 보여주면 사진을 보고, 그리고 대화했던 내용을 참고해서 풍부한 일기를 작성해줘. 일기의 내용 외에는 쓰지마."

conversation_history = {
    "text_prompt": text_prompt,
    "img_prompt": img_prompt,
    "user": [],
    "assistant": []
}

# 직접 지정한 이미지 경로 리스트
image_paths = [
    "./data/fine_tuning_img/003.jpg",
    "./data/fine_tuning_img/004.jpg",
    "./data/fine_tuning_img/005.jpg"
]

# 최종 결과 저장 딕셔너리
final_output = {}
current_date = datetime.now().strftime("%Y-%m-%d")
final_output[current_date] = []

for idx, image_path in enumerate(image_paths):
    print(f"\n🖼️ 현재 이미지: {image_path}")

    # 이미지 인코딩
    with open(image_path, "rb") as img_file:
        encoded_image = base64.b64encode(img_file.read()).decode("utf-8")

    # 이미지 기반 첫 코멘트 받기
    first_comment = generate_first_comment(encoded_image, first_comment_prompt)
    print(f"GPT (첫 인사): {first_comment}")

    # 사용자와 대화 시작 (최대 3회)
    chat_with_gpt(conversation_history,3) # 3=몇번 대화할건지

    # 일기 생성
    print("📝 GPT가 일기를 생성 중입니다...")
    diary_text = generate_diary_with_image(conversation_history, encoded_image)
    print(f"GPT (일기): {diary_text}")

    final_output[current_date].append({
        "image_index": image_path.split("/")[-1].split(".")[0],
        "image_base64": encoded_image,
        "diary": diary_text
    })

# JSON 파일 저장
output_json_path = "./data/diary_output_all.json"
with open(output_json_path, "w", encoding="utf-8") as f:
    json.dump(final_output, f, ensure_ascii=False, indent=2)

print(f"\n✅ 전체 일기가 {output_json_path}에 저장되었습니다.")

# 전체 대화 내역 출력 함수
def print_conversation_history(conversation_history):
    print("\n🗣️ 지금까지의 대화 내역:\n")
    for i in range(len(conversation_history["user"])):
        print(f"User: {conversation_history['user'][i]}")
        if i < len(conversation_history["assistant"]):
            print(f"GPT: {conversation_history['assistant'][i]}")
        print("-")

# 대화 내역 출력
print_conversation_history(conversation_history)
