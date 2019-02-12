from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
from PIL import ImageDraw
import io
from PIL import Image
from PIL import ImageFont


def create_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.96 Safari/537.36")
    chrome_options.binary_location = '/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary'
    # chrome_options.add_argument("user-data-dir=/Users/dmitrii_nikolaev/Library//Application Support/Google/Chrome Canary")

    return webdriver.Chrome(executable_path=os.path.abspath("chromedriver"),   chrome_options=chrome_options)


def draw_on_screen(screen, text):
    img = Image.open(io.BytesIO(screen))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype('/Library/Fonts/Arial Bold.ttf', 46)
    draw.text((100, 170), text, (255, 20, 20), font=font)
    return img
