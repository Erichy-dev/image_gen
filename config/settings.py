import os

# change this to the folder where the excel file is located
DOWNLOADS_FOLDER = '/Users/mac/Downloads/'
# Excel Settings
INPUT_EXCEL_FILE = os.path.join(DOWNLOADS_FOLDER, "template (4).xlsx")

# Image Processing Settings
IMAGE_OUTPUT_SIZE = (3600, 3600)
IMAGE_DPI = (300, 300)
SUPPORTED_IMAGE_FORMATS = ('.png', '.jpg', '.jpeg')

# ... rest of your existing settings ... 