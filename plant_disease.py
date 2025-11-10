from transformers import pipeline
from PIL import Image

# Load the model pipeline
pipe = pipeline(
    "image-classification", 
    model="linkanjarad/mobilenet_v2_1.0_224-plant-disease-identification"
)

# Load a local image
image = Image.open(r"No Defect .jpg")  # replace with your image path

# Run classification
results = pipe(image)

print(results)