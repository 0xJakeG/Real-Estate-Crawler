from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import io
from minio import Minio
from bs4 import BeautifulSoup
import os
import random
import undetected_chromedriver as uc

minio_client = Minio(
        '127.0.0.1:9000',
        access_key='LMaoN5mHeQ7E30sYRgZ9',
        secret_key='3lHDwGUx64Gg5paYADKX3Itf3Z2GTvXYJgMl7p3P',
        secure=False
    )

bucket_name = 'real-estate'

def generate_random_user_agent():
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36',
        # Add more user-agent strings as needed
    ]
    return random.choice(user_agents)

def web_scraping_task():
    headers = {
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Referer': 'https://www.google.com/'
    }
    
    url = 'https://www.realtor.com/realestateandhomes-search/Charlotte_NC'
    
    driver = uc.Chrome(headless=True,use_subprocess=False)

    try:
        driver.get(url)
        
        # Wait for the page to load completely (adjust as needed)
        driver.implicitly_wait(10)
        
        # Print website response (for debugging)
        print("Website Response:")
        print(driver.page_source)
        
        # Get the fully rendered HTML
        html_content = driver.page_source
        
        save_to_minio('search-result-pages/Charlotte_NC/scraped-content-house.html', html_content)
    
    finally:
        driver.quit()


def parse_HTML_To_List_Of_Links():
    
    filepath = 'search-result-pages/Charlotte_NC/scraped-content-house.html'
    soup = get_from_minio(filepath)
    
    tags = soup.find_all('a', href = True)
    allHrefs = []
    for t in tags:
        allHrefs.append(t['href'])
       
    filtered_hrefs = [href for href in allHrefs if '/realestateandhomes-detail/' in href]
        
    
    print(filtered_hrefs)
    print("Number of links: " + str(len(filtered_hrefs)))
    
def get_from_minio(fullfilepath):

    response = minio_client.get_object(bucket_name, fullfilepath)

    html_data = response.data.decode('utf-8')

    response.close()
    response.release_conn()
        
    soup = BeautifulSoup(html_data, 'html.parser')
        
    return soup
    
def save_to_minio(fullfilepath, data):

    if not minio_client.bucket_exists(bucket_name):
        minio_client.make_bucket(bucket_name)

    # Encode the data to bytes
    data_bytes = data.encode('utf-8')

    minio_client.put_object(
        bucket_name, fullfilepath, io.BytesIO(data_bytes), len(data_bytes)
    )

if __name__ == '__main__':
    web_scraping_task()
    #path = 'search-result-pages/Charlotte_NC/scraped-content-house.html'
    #print(get_from_minio(path))
    parse_HTML_To_List_Of_Links()

