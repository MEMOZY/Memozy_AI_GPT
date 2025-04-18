import os
import base64
import json
from openai import OpenAI

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
    api_key="",
)


# 대화 메시지 추가 함수
def add_message(conversation_history, gpt_content, user_content):
    if user_content:
        conversation_history["user"].append(user_content)
    if gpt_content:
        conversation_history["assistant"].append(gpt_content)

# 대화용 GPT API 호출 함수
def chat_with_gpt(conversation_history):
    # 전체 메시지 리스트를 기록하는 임시 캐시역할을 하는 변수 meessages
    # conversation_history로부터 대화 내역을 쭉 가져온다
    messages = [{"role": "user", "content": conversation_history["text_prompt"]}]
    # zip함수로 user와 assistant의 대화 내역을 묶어서 한묶음씩 가져온다
    for user_msg, gpt_msg in zip(conversation_history["user"], conversation_history["assistant"]):
        messages.append({"role": "user", "content": user_msg})
        messages.append({"role": "assistant", "content": gpt_msg})

    # 사용자로부터 입력 받기
    user_input = input("You: ")
    if user_input.strip().lower() == "end":
        return None, False

    # 마지막 사용자 입력 추가
    messages.append({"role": "user", "content": user_input})

    # GPT API 호출
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages
    )

    gpt_response = response.choices[0].message.content.strip()

    # 대화 내역 저장
    add_message(conversation_history, gpt_response, user_input)

    return gpt_response, True

# 대화 내역 기반 + 이미지로부터 GPT 일기 생성
def generate_diary_with_image(conversation_history, image_path, output_json_path="./data/diary_output.json"):
    # 1. 이미지 파일 base64로 인코딩
    with open(image_path, "rb") as img_file:
        encoded_image = base64.b64encode(img_file.read()).decode("utf-8")

    # 2. 이전 대화 내역을 GPT 메시지 형태로 구성
    messages = [{"role": "user", "content": conversation_history["img_prompt"]}]
    for user_msg, assistant_msg in zip(conversation_history["user"], conversation_history["assistant"]):
        messages.append({"role": "user", "content": user_msg})
        messages.append({"role": "assistant", "content": assistant_msg})

    # 3. 이미지와 함께 GPT에게 일기 작성 요청
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

    # 4. GPT API 호출
    response = client.chat.completions.create(
        model="ft:gpt-4o-2024-08-06:personal:capstone150img:BMxNfNjK", #여기에 내가 fine-tuning한 모델을 넣으면 된다. 기본="gpt-4o"
        messages=messages,
        temperature=0.7
    )

    diary_text = response.choices[0].message.content.strip()

    # 5. 결과를 JSON으로 저장
    result = {

        "diary": diary_text,
        "image_base64": encoded_image
    }

    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 일기가 {output_json_path} 파일에 저장되었습니다.")

    return response.choices[0].message.content.strip()

# 초기 프롬프트
text_prompt = "내가 너에게 사진을 주기 전 사진에 대한 정보를 알려줄거야. 내가 너에게 주는 정보를 너는 잘 듣고 나중에 이미지 캡셔닝을 진행할 때 사용해줘. 추가로 궁금한게 중간에 생기면 언제든 물어봐."
img_prompt = "너는 나의 그림일기를 대신 작성해주는 역할이야. 내가 너에게 사진을 보여주면 너는 사진을 보고 그 날 있었던 일기를 간단하게 작성해줘. 이때 위의 대화 내용을 참고해서 일기의 내용을 풍부하게 작성해줘. 일기의 내용 외에는 작성하지마."
# 대화 기록을 저장할 변수 선언
conversation_history = {
    "text_prompt": text_prompt,
    "img_prompt": img_prompt,
    "user": [],
    "assistant": []
}

# 시작 메시지 출력 및 첫 입력 받기
print("GPT: 이 사진에 대해 알려주세요! 어떤 하루를 보냈나요?")

# 대화 루프조절 변수
keep_going = True

# gpt와 대화 계속 하면서 대화 내역 저장
while keep_going:
    gpt_response, keep_going = chat_with_gpt(conversation_history)
    if gpt_response:
        print(f"GPT: {gpt_response}")

# 유저가 'end'입력하면 대화 종료

# 대화 종료 후 이미지 캡션 생성
print("\nGPT: 대화내역을 기반으로 일기를 작성하고 있어요! 잠시만 기다려주세요...")     

# 이미지 경로 설정
image_path = "./data/fine_tuning_img/082.jpg"
# 일기 생성 함수 호출
gpt_diary_output =generate_diary_with_image(conversation_history, image_path)
print(f"최종 일기 생성 내용: {gpt_diary_output}")
