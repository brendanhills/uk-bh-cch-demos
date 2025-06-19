
import vertexai
from vertexai.preview.vision_models import Image, ImageGenerationModel

# TODO(developer): Update and un-comment below lines
# PROJECT_ID = "your-project-id"
# input_file = "input-image.png"
# output_file = "output-image.png"
# prompt = "" # The text prompt describing what you want to see.

vertexai.init(project=PROJECT_ID, location="us-central1")

model = ImageGenerationModel.from_pretrained("imagegeneration@002")
base_img = Image.load_from_file(location=input_file)

images = model.edit_image(
    base_image=base_img,
    prompt=prompt,
    # Optional parameters
    seed=1,
    # Controls the strength of the prompt.
    # -- 0-9 (low strength), 10-20 (medium strength), 21+ (high strength)
    guidance_scale=21,
    number_of_images=1,
)

images[0].save(location=output_file, include_generation_parameters=False)

# Optional. View the edited image in a notebook.
# images[0].show()

print(f"Created output image using {len(images[0]._image_bytes)} bytes")
# Example response:
# Created output image using 1234567 bytes