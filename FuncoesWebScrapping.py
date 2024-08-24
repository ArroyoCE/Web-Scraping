from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fake_headers import Headers
import requests
from bs4 import BeautifulSoup
import time


def extract_html(url):
    header = Headers(
    browser="chrome",  # Generate only Chrome UA
    os="win",  # Generate only Windows platform
    headers=False # generate misc headers
    )
    
    customUserAgent = header.generate()['User-Agent']
    
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920x1080")
    options.add_argument("--window-size=1920x1080")
    options.add_argument('--allow-running-insecure-content')
    options.add_argument(f"user-agent={customUserAgent}")
   

    driver = webdriver.Chrome(options=options) 
    
    
    
    driver.get(url)
    driver.execute_script("window.scrollTo(0, 10000);")
    time.sleep(5)
    

    html_content = driver.page_source
    driver.quit()

    return html_content

def abrir_navegador(url):


    options = Options()
    #options.add_argument("--window-position=20,20") 
    #options.add_argument("--window-size=800,400") 

    driver = webdriver.Chrome(options=options)
    driver.get(url)

    # Wait for 10 seconds or until the user closes the window
    try:
        time.sleep(10)
    except Exception:
        pass

    driver.quit()