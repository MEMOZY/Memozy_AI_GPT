import os
import json

"""
5th step
지금까지 아무 문제가 없었다면 이제 fine tuning을 위한 JSONL 파일을 생성한다

gpt api 모델을 fine-tuning하기 위한 JSONL 파일 생성 코드
1. jsonl 템플릿 생성
2. 이미지 URL을 img2base64.json로부터 파일에서 읽어와서 JSONL 파일에 작성
3. 이미지에 대한 일기 내용을 img_content.json로부터 파일에서 읽어와서 JSONL 파일에 작성
4. for 반복문은 fine_tuning_img 디렉토리 내의 모든 이미지 파일의 갯수
"""



# 프롬프트 작성 구간
general_system_message = {
    "role": "system",
    "content": "너는 나의 그림일기를 대신 작성해주는 역할이야. 내가 너에게 사진을 보여주면 너는 사진을 보고 그 날 있었던 일기를 3문장으로 작성해줘. 일기의 내용 외에는 작성하지마."
}

# 이미지에 대한 일기 내용이 저장된 JSON 파일 읽기
img_content_data = "./data/img_content.json"
with open(img_content_data, "r", encoding="utf-8") as json_file:
    image_content_data = json.load(json_file)

# base64로 인코딩된 이미지 URL이 저장된 JSON 파일 읽기
base64url = "./data/img2base64.json"
with open(base64url, "r", encoding="utf-8") as json_file:
    url_data = json.load(json_file)

# 이미지 파일들이 있는 디렉토리 경로(반복문을 돌릴 때 이미지 갯수를 읽어오기 위해 사용)
directory_path = "./data/fine_tuning_img"
image_files = [f for f in os.listdir(directory_path) if f.lower().endswith((".jpg", ".jpeg", ".png"))]

# gpt api finetuning 학습으로 쓸 JSONL 파일을 저장할 경로
fine_tuning_jsonl_path = "./data/fine_tuning_testData.jsonl"

# JSONL 파일 쓰기
with open(fine_tuning_jsonl_path, "w", encoding="utf-8") as jsonl_file:
    for image_filename in image_files:
        if image_filename in url_data and image_filename in image_content_data:
            entry = {
                "messages": [
                    general_system_message,
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": { "url": url_data[image_filename], "detail": "low" }
                            }
                        ]
                    },
                    { "role": "assistant", "content": image_content_data[image_filename], "weight": 1 }
                ]
            }
            jsonl_file.write(json.dumps(entry, ensure_ascii=False) + "\n")

print(f"Fine-tuning data saved to {fine_tuning_jsonl_path}")
