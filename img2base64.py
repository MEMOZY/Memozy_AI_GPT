import os
import base64
import json
"""
2nd step
인덱스로 표기된 이미지 폴더 내 모든 이미지 파일을 순차적으로 불러와서
Base64 인코딩하여 JSON 파일로 저장하는 코드
"""

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def encode_images_in_directory(directory):
    image_data = {}
    
    for filename in os.listdir(directory):
        if filename.lower().endswith((".jpg", ".jpeg", ".png")):
            image_path = os.path.join(directory, filename)
            base64_image = encode_image(image_path)
            image_data[filename] = f"data:image/jpeg;base64,{base64_image}"
    
    return image_data

# 인코딩 할 이미지들이 있는 디렉토리 경로
directory_path = "./data/fine_tuning_img"

# 이미지 인코딩 수행
encoded_images = encode_images_in_directory(directory_path)

# JSON 파일로 저장
output_json_path = "./data/img2base64.json"
with open(output_json_path, "w", encoding="utf-8") as json_file:
    json.dump(encoded_images, json_file, indent=4)

# 특정 이미지(예: 001.jpg)의 URL 확인
image_filename = "001.jpg"
if image_filename in encoded_images:
    print(f"{image_filename} URL: {encoded_images[image_filename]}")
else:
    print(f"{image_filename} not found in the directory.")