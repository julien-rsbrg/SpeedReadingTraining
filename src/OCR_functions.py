# Code adapted from https://colab.research.google.com/github/mistralai/cookbook/blob/main/mistral/ocr/structured_ocr.ipynb#scrollTo=dxefUpm-Idp8


import os
from pathlib import Path
from dotenv import load_dotenv

from mistralai import Mistral
from mistralai import DocumentURLChunk
from mistralai.models import OCRResponse


load_dotenv()
api_key_value = os.getenv("MISTRAL_API_KEY")


def replace_images_in_markdown(markdown_str: str, images_dict: dict) -> str:
    for img_name, base64_str in images_dict.items():
        markdown_str = markdown_str.replace(f"![{img_name}]({img_name})", f"![{img_name}]({base64_str})")
    return markdown_str



def remove_images_in_markdown(markdown_str: str, images_dict: dict) -> str:
    for img_name, _ in images_dict.items():
        markdown_str = markdown_str.replace(f"![{img_name}]({img_name})", "")
    return markdown_str



def get_combined_markdown(ocr_response: OCRResponse, include_images: bool = False) -> str:
    markdowns: list[str] = []
    for page in ocr_response.pages:
        image_data = {}
        for img in page.images:
            image_data[img.id] = img.image_base64
            
        if include_images:
            markdowns.append(replace_images_in_markdown(page.markdown, image_data))
        else:
            markdowns.append(remove_images_in_markdown(page.markdown, image_data))

    return "\n\n".join(markdowns)



def convert_pdf_to_str(pdf_path:str, include_images:bool = False, api_key: str = api_key_value) -> str:
    pdf_file = Path(pdf_path)
    assert pdf_file.is_file()
    
    # call Mistral to jsonify the pdf
    client = Mistral(api_key=api_key)
    uploaded_file = client.files.upload(
        file={
            "file_name": pdf_file.stem,
            "content": pdf_file.read_bytes(),
        },
        purpose="ocr",
    )

    signed_url = client.files.get_signed_url(file_id=uploaded_file.id, expiry=1)

    pdf_response = client.ocr.process(document=DocumentURLChunk(document_url=signed_url.url), model="mistral-ocr-latest", include_image_base64=True)

    # response_dict = json.loads(pdf_response.json())
    # json_string = json.dumps(response_dict, indent=4)

    return get_combined_markdown(ocr_response=pdf_response,include_images=include_images)


if __name__ == "__main__":
    print(convert_pdf_to_str(pdf_path="test/HAR2024_article_redaction.pdf"))