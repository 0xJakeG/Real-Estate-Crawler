import requests
from minio import Minio
import io
from bs4 import BeautifulSoup


# def web_scraping_task():
#     url = 'https://www.realtor.com/realestateandhomes-detail/2542-Carya-Pond-Ln_Charlotte_NC_28212_M52613-85497?from=srp-list-card'
#     headers = {
#         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
#         'Accept-Language': 'en-US,en;q=0.9',
#         'Accept-Encoding': 'gzip, deflate, br',
#         'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
#         'Connection': 'keep-alive',
#         'Upgrade-Insecure-Requests': '1',
#         'Referer': 'https://www.google.com/'
#     }
#     response = requests.get(url, headers=headers)
    
#     if response.status_code == 200:
#         html_content = response.text
#         save_to_minio('scraped-content-house.html', html_content)
#     else:
#         print(f"Failed to retrieve the website. Status code: {response.status_code}")

def parse_HTML_To_List_Of_Links():
    url = 'https://www.realtor.com/realestateandhomes-search/Charlotte_NC'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Referer': 'https://www.google.com/'
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        html_content = response.text
        
        
    soup = BeautifulSoup(html_content, 'lxml')
    tags = soup.find_all('a')
    print(tags)
    
    

def save_to_minio(filename, data):
    minio_client = Minio(
        '127.0.0.1:9000',
        access_key='LMaoN5mHeQ7E30sYRgZ9',
        secret_key='3lHDwGUx64Gg5paYADKX3Itf3Z2GTvXYJgMl7p3P',
        secure=False
    )

    bucket_name = 'real-estate'
    if not minio_client.bucket_exists(bucket_name):
        minio_client.make_bucket(bucket_name)

    # Encode the data to bytes
    data_bytes = data.encode('utf-8')

    minio_client.put_object(
        bucket_name, filename, io.BytesIO(data_bytes), len(data_bytes)
    )

if __name__ == '__main__':
    parse_HTML_To_List_Of_Links()

