from openai import OpenAI
import base64
import json
import os
from datetime import datetime

"""
최종적으로  gpt api를 이용하여 일기를 생성하고, data 정보를 backend에 보내기 위해 json 파일로 저장하는 테스팅코드
gpt api와 대화를 하며 gpt는 사진에 대한 정보를 사용자로부터 얻고
그 정보를 바탕으로 일기를 생성한다

<logic>
1. gpt api를 2개를 다른 함수로 이용하여 불러온다.(대화용, 이미지 캡션용) 각각 다른 프롬포트를 갖는다.
2. 단순 text를 이용한 대화용 api 호출 함수에서는 사용자와 대화하며 사진에 대한 정보를 얻는다
3. 이때 대화용 api(첫번째)에서는 대화 내역을 딕셔너리에 저장해놓음으로써 추후 일기를 생성할 때 참고한다
4. 대화가 끝나고 일기를 생성할 때는 두번째 이미지 캡션 gpt api에서는 딕셔너리에 저장된 대화 내역을 전부 갖고온다
5. 그리하여 대화 내역을 기반으로 사용자의 이미지로부터 일기를 생성한다
6. 사용자의 이미지를 base64로 인코딩한 이미지 정보와, 일기 내용을 json 파일로 저장한다
"""

client = OpenAI(
    api_key="OPENAI_API_KEY",  
)




# 대화 메시지 추가 함수
def add_message(conversation_history, gpt_content, user_content):
    if user_content:
        conversation_history["user"].append(user_content)
    if gpt_content:
        conversation_history["assistant"].append(gpt_content)

# 대화용 GPT API 호출 함수
def chat_with_gpt(conversation_history):
    messages = [{"role": "user", "content": conversation_history["text_prompt"]}]
    for user_msg, gpt_msg in zip(conversation_history["user"], conversation_history["assistant"]):
        messages.append({"role": "user", "content": user_msg})
        messages.append({"role": "assistant", "content": gpt_msg})

    user_input = input("You: ")
    if user_input.strip().lower() == "end":
        return None, False

    messages.append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages
    )

    gpt_response = response.choices[0].message.content.strip()
    add_message(conversation_history, gpt_response, user_input)

    return gpt_response, True

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
        messages=messages,
        temperature=0.7
    )

    return response.choices[0].message.content.strip()

# 초기 프롬프트
text_prompt = "내가 너에게 사진을 주기 전 사진에 대한 정보를 알려줄거야. 내가 너에게 주는 정보를 너는 잘 듣고 나중에 일기를 작성할 때 사용해줘. 추가로 궁금한게 중간에 생기면 언제든 물어봐. 이전 대화내여을 참고해서 대화해줘. "
img_prompt = "너는 나의 그림일기를 대신 작성해주는 역할이야. 내가 너에게 사진을 보여주면 너는 사진을 보고 그 날 있었던 일기를 간단하게 작성해줘. 이전 대화 내용을 참고해서 이전 내용들을 연결해서 작성해줘. 일기를 풍부하게 작성해줘. 일기의 내용 외에는 작성하지마."

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

    # 사용자와 대화 시작
    keep_going = True
    print("GPT: 이 사진에 대해 알려주세요! 어떤 하루를 보냈나요?")
    while keep_going:
        gpt_response, keep_going = chat_with_gpt(conversation_history)
        if gpt_response:
            print(f"GPT: {gpt_response}")

    # 이미지 인코딩
    with open(image_path, "rb") as img_file:
        encoded_image = base64.b64encode(img_file.read()).decode("utf-8")

    print("\n📝 GPT가 일기를 생성 중입니다...")
    diary_text = generate_diary_with_image(conversation_history, encoded_image)
    print(f"GPT: {diary_text}")

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