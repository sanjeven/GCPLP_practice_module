from recipe_scrapers import scrape_me
import json
import time
import requests
import random
import sys
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


# to minimize getting blocked from scraping
user_agents_list = [
    'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.83 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36'
]

# URL to get new link

URL = "https://www.food.com/search/Singapore"

#####################this portion to retrieve URLS to scrape from a website##################

# Create a request interceptor
def interceptor(request):
    del request.headers['Referer']  # Delete the header first
    del request.headers['User-Agent']  # Delete the header firs
    request.headers['User-Agent'] = random.choice(user_agents_list)

#Initialize chrome driver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

# Set the interceptor on the driver
driver.request_interceptor = interceptor

# Open the  URL in the browser
driver.get(URL)
time.sleep(5)

for _ in range(5):
    driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
    time.sleep(3)  # Wait for the page to load

# Get the page source after loading all content
page_source = driver.page_source
# Close the browser
driver.quit()


# Parse the HTML content of the page | grep all the recipie links
soup = BeautifulSoup(page_source, 'html.parser')
element_list = soup.find_all('h2', class_='title')
f=open("new_links.txt","w" , encoding="utf-8")
for element in element_list:
    f.write("%s\n" % element.a['href'])
f.close()
#######################################################################


# opening the file in read mode and conver to list
old_file = open("old_links.txt", "r")
oldlinks = old_file.read()
O_URLS = oldlinks.split("\n")
old_file.close()

new_file = open("new_links.txt", "r")
newlinks = new_file.read()
N_URLS = newlinks.split("\n")

# find those not scrape before and remove empty string in list
R_URLS=list(set(N_URLS).difference(O_URLS))
R_URLS = list(filter(None, R_URLS))

# if no new link exit
if len(R_URLS) == 0:
    print("No new link")
    sys.exit()
    
    
old_w=open("old_links.txt","a" , encoding="utf-8")

for index, item in enumerate(R_URLS):
    try:
#        print(item)
        recipe = scrape_me(item)
        old_w.write("%s\n" % item)
#        #print(recipe.to_json())
        filename  = "data{}.json".format(index + len(O_URLS))
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(recipe.to_json(), f, ensure_ascii=False, indent=4)
#    
        time.sleep(3)
#        
    except:
        print('Some errors occured')
old_w.close()
     
