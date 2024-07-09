from PIL import Image

image_path = "D:\Project\Test\image\original6.jpg"
try:
    image = Image.open(image_path)
    image.show()
    print("Image opened successfully")
except Exception as e:
    print(f"Error opening image: {e}")