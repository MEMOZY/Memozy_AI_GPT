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
    api_key="OPENAI_API_KEY", 
)

# 형태소 분석 기반 전처리 함수(유저의 입력값, 불용어 txt파일 경로)
def tokenization_stopwords(user_input, stopwords_path="./data/korean_stopWords.txt"):
    # 불용어 파일 읽기
    with open(stopwords_path, "r", encoding="utf-8") as f:
        stop_words = set(line.strip() for line in f if line.strip())

    # 한글, 영어, 숫자, 공백만 유지. 나머지는 user input에서 싹다 제거
    cleaned_text = re.sub(r'[^가-힣a-zA-Z0-9\s]', '', user_input)

    # 형태소 분석 후 조사, 문장부호, 접미사 제거 + 불용어 파일에 있는 단어들도 제거
    tokens = [word for word, pos in okt.pos(cleaned_text, stem=True)
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
너는 사용자의 사진일기에 대해 먼저 사진을 보고 추측하여 사용자로부터 대화를 유도하는 역할이야.
이미지를 보고 '~~한 것같은 사진이네요. 이 사진에 대해 알려주세요!' 라는 식으로 말해.
"""
text_prompt = """
내가 너에게 사진에 대한 정보를 알려줄거야.
너는 잘 듣고 이후 일기 작성할 때 활용해줘.
추가 궁금한 게 있으면 질문해도 좋아.
대화는 이전 내용을 참고해서 자연스럽게 이어가.
사용자가 일기작성과 관련되지 않은 것을 묻거나 말한다면 거절해줘.
"""
img_prompt = """
너는 나의 그림일기를 대신 작성해주는 역할이야.
내가 너에게 사진을 보여주면 사진을 보고, 그리고 대화했던 내용을 참고해서 풍부한 일기를 작성해줘.
비속어를 검열하지 마.
일기를 작성할 때 나의 감정, 기분, 마음가짐을 마음대로 작성하지마.
일기의 내용 외에는 쓰지마.
"""

conversation_history = {
    "text_prompt": text_prompt,
    "img_prompt": img_prompt,
    "user": [],
    "assistant": []
}

# 이미지 경로 설정
image_paths = [
    "./data/fine_tuning_img/003.jpg",
    "./data/fine_tuning_img/004.jpg",
    "./data/fine_tuning_img/005.jpg"
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
