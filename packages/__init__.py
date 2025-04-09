from bs4 import BeautifulSoup
import requests
import sys
import numpy as np
import pandas as pd
import string
from selenium import webdriver 
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
from google import genai
from google.api_core.exceptions import ClientError
from selenium.common.exceptions import (NoSuchElementException, 
                                        StaleElementReferenceException, 
                                        TimeoutException, 
                                        ElementClickInterceptedException,
                                        ElementNotInteractableException)


data_url = [r"https://nhathuoclongchau.com.vn/benh",
            r"https://tamanhhospital.vn/benh-hoc-a-z/",
            r"https://youmed.vn/tin-tuc/trieu-chung-benh/",
            r"https://medlatec.vn/tu-dien-benh-ly",
            r"https://www.vinmec.com/vie/tra-cuu-benh/",
            r"https://benhvienphuongdong.vn/tra-cuu-benh/",
            r"https://dantri.com.vn/tra-cuu-suc-khoe.htm",
            r"https://hellodoctors.vn/chuyen-khoa.html"]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
}

driver = webdriver.Chrome(service=Service(r"M:\\ChromeDriver\\chromedriver-win64\\chromedriver.exe"))


def AIGenerate(content):
    response = clientAI.models.generate_content(model="gemini-2.0-flash", contents=content)
    return response.text


# Helper function

# clean text for better format i guess
def cleanText(chars:list[str]=["*", '\n', "'", "\t"], text=None):
    for char in chars:
        text = text.replace(char, "")
    
    return text


# attempt to call page
def getPage(url):
    response = requests.get(url=url, headers=headers)
    if not response: return 1

    return BeautifulSoup(response.content, 'html5lib')


# Get diseases url
def getData(url: str, expand: dict[By, str]=None, container: dict[By, str]=None):
    """This function leverages the similarity in the design of data containers from the 
    source pages to fetch each section's url and title.

    Args:
        url: str: page URL
        expand: dict[By, str] [optional]: {'how': By, 'props': str} Some section required button click to show more data
        container: dict[By, str] [optional]: {'how': By, 'container': str} Search method along with data container properties

    Returns:
        params: dict[str, str]: :Đ ?
    """
    if not requests.get(url).status_code == 200: return 1
    
    driver.get(url)
    if expand: expandSection(how=expand['how'], tagProperties=expand['props'])
    
    Urls = [x.get_attribute('href') for x in driver.find_element(container['how'], container['container']).find_elements(By.TAG_NAME, "a") if (x.get_attribute('href') and x.text) and not x.text.__contains__("Back")]
    data = [cleanText(text=x.text.strip()) for x in driver.find_element(container['how'], container['container']).find_elements(By.TAG_NAME, "a") if (x.get_attribute('href') and x.text) and not x.text.__contains__("Back")]

    params = dict(zip(data, Urls))
    
    return params

# Some pages require all the hidden section to be expanded before its appear in ROM
def expandSection(how: By, tagProperties: str):
    """ Find and click the expand button so that the page would loads new elements into its DOM

    Args:
        how (By): Finding method, By.XPATH is recommended
        tagProperties (str): element's tag
    """
    while True:
        try: 
            if not WebDriverWait(driver=driver, timeout=2).until(
        EC.presence_of_element_located((how, tagProperties))
        ): break        
        
            btn = driver.find_element(how, tagProperties)    
            ActionChains(driver).move_to_element(btn).perform()
            btn.click()
            time.sleep(0.6)
                
        except (NoSuchElementException, StaleElementReferenceException, TimeoutException, ElementNotInteractableException):
            break
        except ElementClickInterceptedException:
            print("Element not clickable. Retrying...")
        continue


# Apply when data and subSection tags are on the same level.
def IdenLevel(page: BeautifulSoup, contentTag:str):
    """A function to use when Symptom section is vague to locate, check out TamAnh Hospital's page element for clarification. This function would
    locate the Symptom section when the page organizes it data with the same-level tag

    Args:
        page (BeautifulSoup): page's element
        contentTag (str): the element that contains text. For instance, many pages use <h2> to hold their content

    Returns:
        text (str): Should be the symptom
    """
    contents = page.find_all(contentTag)
    targetIdx = next((idx for idx, x in enumerate(contents) if SymptomSection(text=x.text)), None)
    if not targetIdx: return None
    
    contents = contents[targetIdx:]

    symptom = []

    for element in contents[0].find_next_siblings():
        if (element == contents[1] or
            "____" in element.text or
            element.get('href')): break
        symptom.append(cleanText(text=element.text))

    return ' '.join(symptom)


# Helper for IdenLevel
def SymptomSection(text: str):
    """ A helper function for IdenLevel, this function would locate the Symptom section by the logic that it would contains the following keywords 

    Args:
        text (str): text? 

    Returns:
        _type_: _description_
    """
    if (text.__contains__("Dấu hiệu") or
    text.__contains__("Triệu chứng") or
    text.__contains__("Biểu hiện") or 
    text.__contains__("biểu hiện") or
    text.__contains__("triệu chứng") or
    text.__contains__("Biến chứng") or
    text.__contains__("biến chứng") or
    text.__contains__("dấu hiệu")): return 1
    
    return 0


def replaceText(text: str):
    corrections = {
        "Bệnh": "-",
        "về": "-",
        "gan": "-",
        "mật": "-",
        "tụy": "-",
        "Trẻ": "-",
        "em": "-",
        "Xương khớp": "Cơ xương khớp",
        "sơ sinh": "",
        "Sơ sinh": "Nhi",
        "tinh thần": "",
        "hoá": 'hóa'
    }
    for target, replacement in corrections.items():
        text = text.replace(target, replacement)
    
    puncsRemove = str.maketrans("", "", string.punctuation)
    text:str = text.translate(puncsRemove).replace("  "," ")
    return text.strip()
    
