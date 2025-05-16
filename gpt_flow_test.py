from openai import OpenAI
import base64
import json
from datetime import datetime
from PIL import Image
import io
import os
from konlpy.tag import Okt # 형태소 분석기
import re # 텍스트 전처리


okt = Okt() # 형태소 분석을 위한 준비

client = OpenAI(
    api_key="OPENAI_API_KEY", # OPENAI API 키
)

# 형태소 분석 기반 전처리 함수(유저의 입력값, 불용어 txt파일 경로)
def tokenization_stopwords(user_input, stopwords_path="./data/korean_stopWords.txt"):
    # 불용어 파일 읽기
    with open(stopwords_path, "r", encoding="utf-8") as f:
        stop_words = set(line.strip() for line in f if line.strip())

    # 한글, 영어, 숫자, 공백만 유지. 나머지는 user input에서 싹다 제거
    cleaned_text = re.sub(r'[^가-힣a-zA-Z0-9\s]', '', user_input)

    # 형태소 분석 후 조사, 문장부호, 접미사 제거 + 불용어 파일에 있는 단어들도 제거
    tokens = [word for word, pos in okt.pos(cleaned_text, stem=False)
              if pos not in ['Josa', 'Punctuation', 'Suffix'] and word not in stop_words] # Eomi, 어미는 제거하지 않는게 좋을 듯하다

    return ' '.join(tokens) # tokens(리스트 형식)을 공백으로 구분된 문자열로 반환 ex) ['오늘', '밥', '먹었다'] -> '오늘 밥 먹었다' 형태로 변환 후 리턴

# 이미지 크기 줄이기 (이미지 경로, 조절 할 사이즈)
def image_resize(image_path, size=(100, 100)): # 이미지 경로와 사이즈가 인자
    img = Image.open(image_path) # 이미지 경로를 읽기
    img = img.convert("RGB") # RGB로 변환 -> 이미지 확장자마다 가진 정보가 다른데 이를 통일하여 처리하기 위함 
    img_resized = img.resize(size) # 사이즈로 변환
    buffered = io.BytesIO() # 이미지 데이터를 base64로 인코딩하기 위한 버퍼 생성, 버퍼없이 인코딩하면 오류 발생
    img_resized.save(buffered, format="JPEG") 
    return base64.b64encode(buffered.getvalue()).decode("utf-8") # base64로 인코딩하여 문자열로 변환한 값을 리턴

# 대화 메시지 추가
def add_message(conversation_history, gpt_content, user_content):
    if user_content:
        conversation_history["user"].append(user_content)
    if gpt_content:
        conversation_history["assistant"].append(gpt_content)

# 이미지 기반 첫 코멘트 생성
def generate_first_comment(encoded_image, prompt):
    messages = [
        {"role": "system", "content": prompt},
        {
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {
                    "url": f"data:image/jpeg;base64,{encoded_image}",
                    "detail": "low"
                }}
            ]
        }
    ]

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages
    )

    gpt_msg = response.choices[0].message.content.strip()
    add_message(conversation_history, gpt_msg, prompt)
    return gpt_msg

# GPT와의 대화 (최대 3회)
def chat_with_gpt(conversation_history, iter_num=3):
    messages = [{"role": "user", "content": conversation_history["text_prompt"]}]
    for user_msg, gpt_msg in zip(conversation_history["user"], conversation_history["assistant"]):
        messages.append({"role": "user", "content": user_msg})
        messages.append({"role": "assistant", "content": gpt_msg})

    for turn in range(iter_num):
        user_input = input("You: ")
        if user_input.strip().lower() == "end" or turn == iter_num - 1:
            break

        # 유저 입력 전처리하여 GPT및 대화내역에 추가
        processed_input = tokenization_stopwords(user_input)

        messages.append({"role": "user", "content": processed_input})

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages
        )

        gpt_response = response.choices[0].message.content.strip()
        add_message(conversation_history, gpt_response, processed_input)

        print(f"GPT: {gpt_response}")

        messages.append({"role": "assistant", "content": gpt_response})

    print("\n💬 대화가 종료되었습니다. 이제 일기를 생성할게요!\n")

# GPT 일기 생성
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
    )

    return response.choices[0].message.content.strip()

# 프롬프트 설정
first_comment_prompt = """
역할(Role):

당신은 사용자의 사진일기를 작성하기 위해 필요한 정보를 수집하는 대화형 어시스턴트입니다.
목표(Goal):

사용자가 제공한 사진을 보고 대화를 유도하여 필요한 정보를 수집합니다.

지시사항(Instructions):
- 사용자가 제공한 사진을 보고, 그 사진에 대한 첫 인사를 작성하세요.
- 사용자가 제공한 사진을 보고, 그 사진에 대해 추측하여 대화를 유도하세요.
- 배경사진이라면 주로 어떤 장소인지 음식사진이라면 어떤 음식인지에 대해 추측하고 물어보세요.

출력 형식(Output Format):
"안녕하세요! 이 사진은 [장소/음식]에서 찍힌 것 같아요. [장소/음식]에 대해 더 이야기해 주실 수 있나요?"
"""
text_prompt = """
역할(Role):
당신은 사용자의 사진일기를 작성하기 위해 필요한 정보를 수집하는 대화형 어시스턴트입니다.

목표(Goal):
사용자가 제공한 사진에 대한 일기를 작성하기 위해 필수 정보를 수집합니다.

지시사항(Instructions):

- 사용자에게 다음의 필수 정보를 질문하여 수집하세요:

    1. 사진이 촬영된 시간대(대략적으로 아침 오후 저녁 어떤 것인지)

    2. 사진이 촬영된 장소, 배경

    3. 이 때 누구와 함께 하였는지

    4. 이 때 기분은 어땠는지

    5. 어떤 일이 있었는지

- 너는 위의 6가지 정보를 얻기 위해 자연스럽게 대화를 유도하고, 필요한 정보가 빠졌다면 추가로 질문해야 해.
- 이때 너는 단도 직입적으로 묻지말고 자연스럽게 대화를 하며 위의 정보를 알아낼 수 있도록 친근하게 물어봐야해.



- 사용자의 입력이 사진과 관련이 없거나 일기 작성과 무관한 경우, 다음과 같이 정중하게 안내하세요:
"죄송하지만, 이 대화는 사진일기를 작성하기 위한 것입니다. 사진과 관련된 이야기로 다시 말씀해 주세요."

- 일기를 작성할만큼의 충분한 정보가 모인 경우, 다음과 같이 정중하게 안내하세요:
"감사합니다. 현재 정보로 이제 일기를 작성할 수 있을 것 같아요! 혹시 알려주실 정보가 더 있나요?"

- 사용자의 감정이나 기분을 네가 임의로 추측하지 마.
- 사용자의 답변을 왜곡하지마
- 사용자의 답변에 의구심을 품지마

출력 형식(Output Format):

질문 기회는 3번밖에 없으므로 너는 이 질문에 대한 답을 알아내도록 압축해서 보내야할거야.
사용자가 질문에 압박을 느끼지 않도록 한번에 너무 많은 질문을 한번에 하지마.
"""





img_prompt = """
역할(Role):
당신은 사용자의 사진일기를 대신 작성하는 어시스턴트입니다.

목표(Goal):
사용자가 제공한 사진과 대화에서 수집한 정보를 바탕으로 자연스럽고 일상적인 느낌의 일기를 작성합니다.

지시사항(Instructions):

- 수집한 정보를 기반으로 일기를 작성하되, 사용자의 감정이나 기분을 추측하지 마세요.

- 사용자가 제공하지 않은 정보를 임의로 추가하지 마세요.

- 일기는 자연스럽고 일상적인 말투로 작성하세요.

- 비속어나 검열은 하지 않아도 괜찮지만, 일기의 흐름에 맞게 자연스럽게 표현하세요.

- 일기의 내용 외에는 추가하지 마세요.(해석, 주석, 부연 설명 없이 순수한 일기 형태로 작성)

출력 형식(Output Format):
자연스럽고 일상적인 말투로 작성된 일기를 제공합니다.
일기의 내용 외에는 출력하지 마세요.(해석, 주석, 부연 설명 없이 순수한 일기 형태로 출력하세요)
"""

conversation_history = {
    "text_prompt": text_prompt,
    "img_prompt": img_prompt,
    "user": [],
    "assistant": []
}

# 이미지 경로 설정
image_paths = [
    "./data/fine_tuning_img/002.jpg", #인물
    "./data/fine_tuning_img/003.jpg", #풍경
    "./data/fine_tuning_img/005.jpg" #음식
]
# stop words들이 쭉 적혀있는 경로 설정
stopwords_path = "./data/korean_stopWords.txt"

final_output = {}
current_date = datetime.now().strftime("%Y-%m-%d")
final_output[current_date] = []

# 전체 프로세스 실행
for idx, image_path in enumerate(image_paths):
    print(f"\n🖼️ 현재 이미지: {image_path}")

    # 이미지 크기 변경 및 인코딩 처리
    encoded_image = image_resize(image_path)

    # 첫 코멘트
    first_comment = generate_first_comment(encoded_image, first_comment_prompt)
    print(f"GPT (첫 인사): {first_comment}")

    # 대화
    chat_with_gpt(conversation_history, 3)

    # 일기 생성
    print("📝 GPT가 일기를 생성 중입니다...")
    diary_text = generate_diary_with_image(conversation_history, encoded_image)
    print(f"GPT (일기): {diary_text}")

    final_output[current_date].append({
        "image_index": os.path.basename(image_path).split(".")[0],
        "image_base64": encoded_image,
        "diary": diary_text
    })

# JSON 저장
output_json_path = "./data/diary_output_all.json"
with open(output_json_path, "w", encoding="utf-8") as f:
    json.dump(final_output, f, ensure_ascii=False, indent=2)

print(f"\n✅ 전체 일기가 {output_json_path}에 저장되었습니다.")

# 대화 내역 출력
def print_conversation_history(conversation_history):
    print("\n🗣️ 지금까지의 대화 내역:\n")
    for i in range(len(conversation_history["user"])):
        print(f"User: {conversation_history['user'][i]}")
        if i < len(conversation_history["assistant"]):
            print(f"GPT: {conversation_history['assistant'][i]}")
        print("-")

print_conversation_history(conversation_history)
