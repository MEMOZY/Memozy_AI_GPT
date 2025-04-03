import base64
from openai import OpenAI

client = OpenAI(
    api_key="OPEN_AI_KEY",
)

# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


# Path to your image
image_path = "./data/test.jpg"



# Getting the Base64 string
base64_image = encode_image(image_path)

prompt="이 사진에 대해 설명해줘"
completion = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
            "role": "user",
            "content": [
                { "type": "text", "text": prompt },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}",
                    },
                },
            ],
        }
    ],
)

print(completion.choices[0].message.content)