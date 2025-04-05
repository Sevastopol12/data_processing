from packages import *

# Fetch data from different data source
# Keep in mind that each page requires different scraping method. For instance, some pages may organize in such manner that showed 
# a list of existed departments followed by diseases list inside, whilst some just have their own department and disease appear in one page
# Checking LongChau and YouMed for better clarification

#Long Chau
def getLC(url=data_url[0]):
    subDF = pd.DataFrame({"Disease": [], "Department":[], "Symptom":[]})
    meineDepartments = getData(url, 
                               expand={'how': By.XPATH, 'props': "//div[contains(text(), 'Xem thêm ')]"}, 
                               container={'how': By.XPATH, "container":"//div[@class='pt-6 umd:py-4 relative z-[2]']"})

    for department, departmentUrl in meineDepartments.items():
        diseases = getData(url=departmentUrl, 
                           expand={'how': By.XPATH, 'props': "//span[contains(text(), 'Xem thêm')]"},
                           container={'how': By.XPATH, "container":"//div[@class='grid grid-cols-2 omd:grid-cols-4 gap-2 omd:gap-5 umd:pt-4 ']"})

        for disease, diseaseUrl in diseases.items():
            page = getPage(url=diseaseUrl)
            symptom = ' '.join([x.text for x in page.find("div", id='symptom').find_all(["h2", "h3", "p", "li"]) if not any(item in x.text for item in ["bác sĩ", "Hình ảnh", "Xem thêm"])])
            subDF.loc[len(subDF)] = [disease, department, symptom]

    
    return subDF


#TamAnh Hospital
def getTA(url=data_url[1]):
    df = pd.DataFrame({"Disease": [], "Department":[], "Symptom":[]})
    
    diseaseUrl = getData(url=url, expand=None, container={"how": By.XPATH, 'container': "//div[@class='content_az']"})
    
    for disease, diseaseUrl in diseaseUrl.items():
        print(diseaseUrl)
        page = getPage(diseaseUrl)
        department = [cleanText(text=x.text.strip()) for x in page.find("nav", class_='rank-math-breadcrumb').find_all("a") if x.get('href')][-1]
        
        # Extract information
        symptom = IdenLevel(page=page, contentTag="h2")

        df.loc[len(df)] = [disease, department, symptom]

    return df

#YouMed
def getYM(url=data_url[2]):
    subDF = pd.DataFrame({"Disease": [], "Department":[], "Symptom":[]})
    
    diseaseUrl = getData(url=url, expand=None, container={"how": By.XPATH, 'container': "//div[@class='items-inner']"})
    
    for disease, diseaseUrl in diseaseUrl.items():
        page = getPage(url=diseaseUrl)
        department = page.find("div", class_='container pt-4').text.split(" / ")[1]
        
        # Extract information
        symptom = IdenLevel(page=page, contentTag="h2")
        subDF.loc[len(subDF)] = [disease, department, symptom]
        
    return subDF

#MedlaTec
def getMLT(url=data_url[3]):
    subDF = pd.DataFrame({"Disease": [], "Department":[], "Symptom":[]})
    department = None
    page = BeautifulSoup(requests.get(url=url).content, 'html5lib')
    diseaseUrl = [x.get('href') for x in page.find("ul", class_="disease-list").find_all("a") if x.get('href')]
    disease = [cleanText(text=x.text.strip()) for x in page.find("ul", class_="disease-list").find_all("a") if x.get('href')]
    
    for disease, diseaseUrl in zip(disease, diseaseUrl):
        try: 
            page = getPage(url=f"{url+'/'+diseaseUrl.split("/")[-1]}")

        # Extract information
            symptomSection = page.find("section", id='disease-symptoms_free')
            symptom = cleanText(text=symptomSection.find("div", class_='body collapsible-target content-show').text.strip())
            subDF.loc[len(subDF)] = [disease, department, symptom]
        
        except AttributeError:
            pass
        
    return subDF    

#VinMec
def getVM(url=data_url[4]):
    subDF = pd.DataFrame({"Disease": [], "Department":[], "Symptom":[]})
    department = None
    alphabet = string.ascii_lowercase
    params = {}
    for char in alphabet:
        pageNum = 1
        while True:
            page = getPage(f"{url}{char}/page_{pageNum}")
            diseasesUrl = [f"https://www.vinmec.com/{x.get('href')}" for x in page.find("ul", class_='list_result_AZ flex').find_all("a") if x.get('href')]
            if len(diseasesUrl) < 1: break
            diseases = [x.text for x in page.find("ul", class_='list_result_AZ flex').find_all("a") if x.get('href')]
            
            for i,j in zip(diseases, diseasesUrl):
                params[i] = j
            
            pageNum +=1
                
        for i in diseasesUrl:
            print(i)
    
    for disease, diseaseUrl in params.items():
        page = getPage(diseaseUrl)
        symptom = [cleanText(text=x.text) for x in page.find_all("div", class_="item_detial_sick") if SymptomSection(text=x.text)]
        
        subDF.loc[len(subDF)] = [disease, department, ','.join(symptom)]
            
    return subDF
                
                    
#PhuongDong Hospital                    
def getPD(url=data_url[5]):
    subDF = pd.DataFrame({"Disease": [], "Department":[], "Symptom":[]})
    page = getPage(url=url)
    container = page.find_all("div", class_='section-item-search mt-3 mt-xl-4 pt-2')

    meineURL = []
    meineDisease = []

    for content in container:
        subURL = [x.get('href') for x in content.find_all("a") if x.get('href')]
        subDisease = [cleanText(text=x.text) for x in content.find_all("a") if x.get('href')]
        meineURL.extend(subURL)
        meineDisease.extend(subDisease)
        
    params = dict(zip(meineDisease, meineURL))

    for disease, diseaseURL in params.items():
        page = getPage(url=diseaseURL)        
        department = [x.text for x in page.find("ol", class_='breadcrumb').find_all("a")][-1]

        symptom = IdenLevel(page=page, contentTag="h2")
        subDF.loc[len(subDF)] = [disease, department, symptom]
    return subDF
        
    
#DanTri news
def getDT(url=data_url[6]):
    subDF = pd.DataFrame({"Disease": [], "Department":[], "Symptom":[]})
    driver.get(url=url)
    expandProps = "//button[@class='dt-p-1 dt-rounded-lg dt-bg-tara btn-swiper btn-swiper-next']"
    containerProps = "//div[@class='swiper-slide swiper-slide-active']"
    
    name = []
    urls = []

    while True:
        try:      
            name.extend('\n'.join([x.text for x in driver.find_element(By.XPATH, containerProps).find_elements(By.CSS_SELECTOR, "div:not([class]):not([id])")]).split("\n"))
            urls.extend([x.get_attribute('href') for x in driver.find_element(By.XPATH, containerProps).find_elements(By.TAG_NAME, "a")])
            
            if not WebDriverWait(driver=driver, timeout=2).until(
        EC.presence_of_element_located((By.XPATH, expandProps))
        ): break        
        
            btn = driver.find_element(By.XPATH, expandProps)    
            ActionChains(driver).move_to_element(btn).perform()
            btn.click()
            time.sleep(0.5)
                
        except (NoSuchElementException, StaleElementReferenceException, TimeoutException, ElementNotInteractableException):
            break
        except ElementClickInterceptedException:
            print("Element not clickable. Retrying...")
        continue
    
    
    diseases = dict(zip([x for x in name if name.index(x)%6 !=0], urls))
    departments = [x for x in name if name.index(x)%6 ==0]

    i = 0
    department = departments[i]
    for disease, diseaseUrl in diseases.items():
        if (i!=0 and i%5==0): department = departments[i//5]
    
        driver.get(diseaseUrl)

        symptom = driver.find_element(By.XPATH, "//h2[@id='disease-symptoms_free']").find_element(By.XPATH, "following-sibling::*[1]").text.replace("\n", " ")
        subDF.loc[len(subDF)] = [disease, department, symptom]
        i += 1
    return subDF
    

#HelloDucktah
def getHelloDoctor(url=data_url[7]):
    subDF = pd.DataFrame({"Disease": [], "Department":[], "Symptom":[]})
    departmentContainer = {'how': By.XPATH, 'container': "//div[@class='department']"}
    meineDepartment = getData(url=url, container=departmentContainer)
    
    for department, departmentURL in meineDepartment.items():
        try:    
            diseaseContainer = {'how': By.XPATH, 'container': "//div[@class='listIllness']"}
            meineDisease = getData(url=departmentURL, container=diseaseContainer)
            
            for disease, diseaseURL in meineDisease.items():
                symptom = IdenLevel(page=getPage(url=diseaseURL), contentTag="h3")
            
                subDF.loc[len(subDF)] = [disease, department, symptom]
        except (NoSuchElementException):
            continue

    return subDF
