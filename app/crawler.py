import io
from minio import Minio
from bs4 import BeautifulSoup
import random
#import undetected_chromedriver as uc
from seleniumbase import Driver as uc
import time

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

def web_scraping_task(city_name):
    start_time = time.time()  # Record the start time

    # Construct the URL based on the city name
    base_url = f'https://www.realtor.com/realestateandhomes-search/{city_name.replace(",", "").replace(" ", "_")}'
    
    headers = {
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Referer': 'https://www.google.com/'
    }

    driver = uc(uc_cdp=True, incognito=True)

    try:
        driver.get(base_url)

        def scroll_to_top(driver):
            driver.execute_script("window.scrollTo(0, 0);")  # Scroll to the top of the page
        
        def scroll_down_custom(driver, scroll_amount=1200, num_scrolls=6, scroll_pause_time=.1):
            for _ in range(num_scrolls):
                # Scroll down by the specified amount
                driver.execute_script(f"window.scrollBy(0, {scroll_amount});")

                # Wait for a short pause to allow content to load
                time.sleep(scroll_pause_time)

        scroll_down_custom(driver)
        scroll_to_top(driver)  # Scroll to the top before starting on the next page
        # Extract the HTML content after scrolling
        html_content = driver.page_source

        # Save the HTML content for the first page
        save_to_minio(f'search-result-pages/{city_name}/scraped-content-page.html', html_content)

        # Parse the HTML content to find the number of pages
        #amount_of_pages = parse_HTML_To_Number_Of_Pages(html_content, "base__StyledAnchor-rui__ermeke-0 klOELo pagination-item")
        amount_of_pages = 5
        print(amount_of_pages)
        all_links = []  # Initialize list to store all links
        links_on_page = parse_HTML_To_List_Of_Links(city_name)
        all_links.extend(links_on_page)
        
        # Iterate through each page and perform scraping
        for page_number in range(2, amount_of_pages + 1):  # Start from page 2, as we've already scraped page 1
            url = f"{base_url}/pg-{page_number}"
            driver.get(url)      
            # Scroll down on the current page
            scroll_down_custom(driver)
            
            # Extract the HTML content after scrolling
            html_content = driver.page_source
            
            # Save the HTML content for the current page
            save_to_minio(f'search-result-pages/{city_name}/scraped-content-page-{page_number}.html', html_content)

            scroll_to_top(driver)  # Scroll to the top before starting on the next page
            # Now you can perform scraping logic for each page as needed
            # For example:
            links_on_page = parse_HTML_To_List_Of_Links(city_name, page_number)
            all_links.extend(links_on_page)

    finally:
        try:
            driver.quit()
        except OSError as e:
            print(f"Error quitting the driver: {e}")

    end_time = time.time()  # Record the end time
    elapsed_time = end_time - start_time  # Calculate elapsed time
    print(f"Task for {city_name} completed in {elapsed_time} seconds.")
    print(len(all_links))
    print(all_links)
def parse_HTML_To_List_Of_Links(city_name, page_number=None):
    if page_number is None:
        filepath = f'search-result-pages/{city_name}/scraped-content-page.html'
    else:
        filepath = f'search-result-pages/{city_name}/scraped-content-page-{page_number}.html'
    
    soup = get_from_minio(filepath)
    
    tags = soup.find_all('a', href=True)
    all_hrefs = []
    for tag in tags:
        all_hrefs.append(tag['href'])
       
    filtered_hrefs = [href for href in all_hrefs if '/realestateandhomes-detail/' in href]
    
    # Convert the list to a set to remove duplicates and then back to a list
    unique_filtered_hrefs = list(set(filtered_hrefs))
    
    # Prepend "https://www.realtor.com" to each link
    unique_filtered_hrefs = ['https://www.realtor.com' + href for href in unique_filtered_hrefs]
    
    print("Number of unique links:", len(unique_filtered_hrefs))
    return unique_filtered_hrefs
    
def parse_HTML_To_Number_Of_Pages(html_data, class_name):
    soup = BeautifulSoup(html_data, 'html.parser') 
    # Find all anchor tags with the specified class
    tags = soup.find_all('a', class_=class_name)
    
    # List to store extracted page numbers
    page_numbers = []

    # Parse the list of anchor tags to extract the page numbers
    for tag in tags:
        aria_label = tag.get('aria-label')
        href = tag.get('href')
        page_number = None
        if aria_label:
            # Extract page number from aria-label
            page_number = int(aria_label.split()[-1])
        elif href:
            # Extract page number from href
            page_number = int(href.split('-')[-1].replace("pg", ""))
        
        # Append the extracted page number to the list
        if page_number is not None:
            page_numbers.append(page_number)
    page_numbers.reverse()  # Reverse the list of page numbers
        
    # Check if the list of page numbers is not empty
    if page_numbers:
        max_page = max(page_numbers)  # Find the maximum page number
    else:
        max_page = None

    return max_page
    
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
    city_name = "Charlotte_NC"
    web_scraping_task(city_name)
    #parse_HTML_To_List_Of_Links(city_name)

