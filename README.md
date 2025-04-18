# Memozy_AI_GPT
# 🎨 GPT API for Image Captioning Fine-tuning

이 리포지토리는 🖼️ GPT API를 활용한 이미지 캡셔닝 모델을 파인튜닝하기 위한 환경을 제공하기위해 만들어졌습니다

## 📂 파일 구조 설명
📁data </br>
├── 📂 fine_tuning_img:처리된 이미지들이 들어있는 디렉토리</br></br>
├── 📂 img: 원본 이미지들이 있는 디렉토리</br></br>
├── 📄 completed_fine_tuning_Data.jsonl: GPT 파인튜닝을 위한 완성된 데이터셋</br></br>
├── 📄 diary_output.json: 최종적으로 테스팅 된 이미지 정보와 캡션 정보를 백엔드에 보낼 테스팅 json파일</br></br>
├── 📄 img_content.json: 이미지 캡션 데이터</br></br>
└── 📄 img2base64.json: 인덱스 처리된 이미지를 base64로 인코딩한 데이터셋</br></br>
</br>

├── 📝 gpt_api_base64_test.py: base64 인코딩 데이터를 이용한 GPT API 이미지 캡션 테스트 코드</br></br>

├── 📝 gpt_api_img_test.py: 이미지를 사용한 GPT API 이미지 캡션 테스트 코드</br></br>

├── 📝 gpt_api_text_test.py: GPT API 텍스트 대화 테스트 코드</br></br>

├── 📝 gpt_flow_test.py: GPT API를 이용하여 맥락을 구성하여 대화내용 기반으로 이미지 일기를 생성하는 최종 테스팅 코드</br></br>

├── 🛠️ image_content_generate.py: img_content.json을 생성하는 코드</br></br>

├── 🛠️ img_indexing.py: 이미지 인덱싱 및 저장 코드</br></br>

├── 🛠️ img2base64.py: img2base64.json 생성 및 base64 인코딩 코드</br></br>

├── 🛠️ make_fine_tuning_data.py: 최종 파인튜닝 데이터를 생성하는 코드</br></br>

└── 🔍 show_image_test.py: 인코딩 정보와 이미지 캡션 매칭 확인 코드</br></br>


## 🚀 사용 방법

1.  이미지를 `data/img` 폴더에 저장합니다.</br></br>
2. `img_indexing.py`를 실행하여 이미지 인덱싱을 수행합니다.</br></br>
3. `img2base64.py`를 실행하여 이미지를 base64로 인코딩하고 `img2base64.json`에 저장합니다.</br></br>
4. `image_content_generate.py`를 실행하여 `img_content.json`을 생성한 후, 사용자가 캡션을 작성합니다.</br></br>
5. `show_image_test.py`를 실행하여 인코딩 정보와 이미지 캡션의 매칭을 확인합니다.</br></br>
6.  이상이 없으면, `make_fine_tuning_data.py`를 실행하여 GPT API 파인튜닝 데이터 `completed_fine_tuning_Data.jsonl`을 생성합니다.

## 최종 결과
<사용 이미지>  
<img src="https://github.com/user-attachments/assets/8a7d6c25-8695-495b-8a22-61fe12a6c3c6" width="400"/>

<대화 내역>
![result](https://github.com/user-attachments/assets/cd8be803-6f8b-47dd-bbe2-4877caab4a31)

