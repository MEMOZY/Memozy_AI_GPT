import json
import base64
from io import BytesIO
from PIL import Image
"""
4th step
최종적으로
base64로 인코딩된 이미지 + 일기 내용이 저장된 JSON 파일을 읽어온다
인코딩된 이미지와 그 이미지의 content를 표시한다
이미지 인코딩 인덱스와 content인덱스가 일치하여 잘 표시되는지 확인하는 코드이다
"""

# Base64 이미지를 디코딩하여 표시하는 함수
def show_base64_image(base64_string):
    image_data = base64.b64decode(base64_string)
    image = Image.open(BytesIO(image_data))
    image.show()

# 이미지 url이 저장된 JSON 파일 읽기
base64_json_path = "./data/img2base64.json"
with open(base64_json_path, "r", encoding="utf-8") as json_file:
    image_data = json.load(json_file)

# 이미지에 대한 일기 내용이 저장된 JSON 파일 읽기
img_content_data = "./data/img_content.json"
with open(img_content_data, "r", encoding="utf-8") as json_file:
    image_content_data = json.load(json_file)

# 1번에서 n번까지의 이미지 순차적으로 디코딩 후 표시
n = 3
for i, (filename, base64_url) in enumerate(image_data.items()):
    if i >= n:
        break
    # Base64 데이터 추출 ("data:image/jpeg;base64," 제거)
    base64_string = base64_url.split(",")[-1]
    
    print(f"Displaying: {filename}")  # 현재 표시 중인 파일 이름 출력
    show_base64_image(base64_string)
    
    # 이미지에 해당하는 일기 내용 출력
    if filename in image_content_data:
        print(f"Content: {image_content_data[filename]}\n")
    else:
        print("No content available for this image.\n")