### class for scanning a recipe png for all the information
### uses openAI gpt vision model to extract text from image

from openai import OpenAI
import base64


class RecipeReader:
    # TODO: should we jjust accept the encoded images? instead of paths?
    prompt = """These are pictures of a recipe. Extract the title, ingredients, and instructions of the recipe from the images. Return them in a json format. Do not say anything else, just respond with a json style dictionary."""

    def __init__(self, image_paths=[], image_encodings=[]):

        if image_paths != [] and image_encodings != []:
            raise ValueError("Provide either image paths or image encodings, not both.")

        if image_paths:
            self.image_paths = image_paths
            self.encode_images()
        elif image_encodings:
            self.encoded_images = image_encodings
        else:
            raise ValueError("Provide either image paths or image encodings.")

        self.client = OpenAI()

    def encode_images(self):

        encodings = []

        for image_path in self.image_paths:
            with open(image_path, "rb") as image:
                encodings.append(base64.b64encode(image.read()).decode("utf-8"))

        self.encoded_images = encodings

    def extract_info(self):

        content = [{"type": "text", "text": self.prompt}]

        for encoding in self.encoded_images:
            content.append(
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "data:image/png;base64," + encoding,
                        "detail": "low",  # TODO: is this good enough resolution? will reduce costs and speed up response time.
                    },
                }
            )

        response = self.client.chat.completions.create(
            model="gpt-4-turbo", messages=[{"role": "user", "content": content}]
        )

        return response.choices[0].message.content
