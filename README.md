# Memozy_AI_GPT
# 🎨 GPT API for Image Captioning Fine-tuning

이 리포지토리는 🖼️ GPT API를 활용한 이미지 캡셔닝 모델을 파인튜닝하기 위한 환경을 제공합니다. 각종 데이터를 준비하고 활용하여 멋진 이미지 캡션 기능을 개발해보세요! ✨

## 📂 파일 구조 설명
📁data </br>
│   ├── 📂 fine_tuning_img:처리된 이미지들이 들어있는 디렉토리</br>
│   ├── 📂 img: 원본 이미지들이 있는 디렉토리</br>
│   ├── 📄 completed_fine_tuning_Data.jsonl: GPT 파인튜닝을 위한 완성된 데이터셋</br>
│   ├── 📄 img_content.json: 이미지 캡션 데이터</br>
│   └── 📄 img2base64.json: 인덱스 처리된 이미지를 base64로 인코딩한 데이터셋</br>
</br>
|
├── 📝 gpt_api_base64_test.py: base64 인코딩 데이터를 이용한 GPT API 이미지 캡션 테스트 코드</br>
|
├── 📝 gpt_api_img_test.py: 이미지를 사용한 GPT API 이미지 캡션 테스트 코드</br>
|
├── 📝 gpt_api_text_test.py: GPT API 텍스트 대화 테스트 코드</br>
|
├── 🛠️ image_content_generate.py: img_content.json을 생성하는 코드</br>
|
├── 🛠️ img_indexing.py: 이미지 인덱싱 및 저장 코드</br>
|
├── 🛠️ img2base64.py: img2base64.json 생성 및 base64 인코딩 코드</br>
|
├── 🛠️ make_fine_tuning_data.py: 최종 파인튜닝 데이터를 생성하는 코드</br>
|
└── 🔍 show_image_test.py: 인코딩 정보와 이미지 캡션 매칭 확인 코드</br>


## 🚀 사용 방법

1.  이미지를 `data/img` 폴더에 저장합니다.</br></br>
2. `img_indexing.py`를 실행하여 이미지 인덱싱을 수행합니다.</br></br>
3. `img2base64.py`를 실행하여 이미지를 base64로 인코딩하고 `img2base64.json`에 저장합니다.</br></br>
4. `image_content_generate.py`를 실행하여 `img_content.json`을 생성한 후, 사용자가 캡션을 작성합니다.</br></br>
5. `show_image_test.py`를 실행하여 인코딩 정보와 이미지 캡션의 매칭을 확인합니다.</br></br>
6.  이상이 없으면, `make_fine_tuning_data.py`를 실행하여 GPT API 파인튜닝 데이터 `completed_fine_tuning_Data.jsonl`을 생성합니다.

