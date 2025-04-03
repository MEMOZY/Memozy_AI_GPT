import os
import json
"""
3rd step

이미지 폴더 내 모든 이미지 파일을 순차적으로 불러와서
이미지에 일기를 작성할 템플릿을 만드는 코드
이후 생성된 템플릿 img_content.json에 일기 직접 쓰면 된다
"""

def content_gen(directory):
    image_data = {}
    i=0
    for filename in os.listdir(directory):
        i+=1
        if filename.lower().endswith((".jpg", ".jpeg", ".png")):
            # image_data[filename] = f"{i} diary content."
            # 테스트로 말 안듣는 gpt 만들어보기
            image_data[filename] = f"No"
    
    return image_data

# 인덱싱된 이미지들이 있는 디렉토리 경로
directory_path = "./data/fine_tuning_img"

# 인덱싱된 이미지들 content 템플릿 생성
contented_images = content_gen(directory_path)

# JSON 파일로 저장
#저장할 파일이름 설정, 단, 일기 작성시 이 코드를 돌리면 내용이 다 날아가기에 작성중인 json파일과 이름을 다르게 지정하도록
output_json_path = "./data/img_content_test.json" 
with open(output_json_path, "w", encoding="utf-8") as json_file:
    json.dump(contented_images, json_file, indent=4)

# 특정 이미지(예: 001.jpg)의 URL 확인
image_filename = "001.jpg"
if image_filename in contented_images:
    print(f"{image_filename} URL: {contented_images[image_filename]}")
else:
    print(f"{image_filename} not found in the directory.")