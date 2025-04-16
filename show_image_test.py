import json
import base64
from io import BytesIO
from PIL import Image
import matplotlib.pyplot as plt

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
    
    # matplotlib로 이미지 표시
    plt.imshow(image)
    plt.axis('off')
    plt.show()

# 이미지 url이 저장된 JSON 파일 읽기
base64_json_path = "./data/img2base64.json"
with open(base64_json_path, "r", encoding="utf-8") as json_file:
    image_data = json.load(json_file)

# 이미지에 대한 일기 내용이 저장된 JSON 파일 읽기
img_content_data = "./data/img_content.json"
with open(img_content_data, "r", encoding="utf-8") as json_file:
    image_content_data = json.load(json_file)

# 150번째 이미지 표시 (인덱스 149)
target_index = 135
image_items = list(image_data.items())

if target_index < len(image_items):
    filename, base64_url = image_items[target_index]
    base64_string = base64_url.split(",")[-1]

    if filename in image_content_data:
        print(f"Content: {image_content_data[filename]}\n")
    else:
        print("No content available for this image.\n")
        
    print(f"Displaying: {filename}")
    show_base64_image(base64_string)


else:
    print("Index out of range. 해당 인덱스의 이미지가 존재하지 않습니다.")

