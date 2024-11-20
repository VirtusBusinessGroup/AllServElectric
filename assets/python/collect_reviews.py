import time
import pandas as pd
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains


HOME_ADVISOR = "https://www.homeadvisor.com/rated.AllServiceElectrical.38781038.html"
YELP = "https://www.yelp.com/biz/all-services-electrical-los-angeles#reviews"


def home_advisor_reviews(link):
    
    # Create a dataframe to store the reviews
    review_data = pd.DataFrame(columns=["Rating", "Name", "Location", "Date", "Service", "Review"])
    
    # Create a ChromeOptions object
    chrome_options = Options()
    
    # Create a ChromeService object
    # service = webdriver.chrome.service.Service(ChromeDriverManager(driver_version = "131.0.6778.86").install())
    service = webdriver.chrome.service.Service(ChromeDriverManager().install())
    
    # Create a ChromeDriver object
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Open the website
    driver.get(link)
    
    # Wait for the page to load
    time.sleep(2)

    # Get the html of the page
    page = driver.page_source
    
    # Parse the html using BeautifulSoup
    soup = BeautifulSoup(page, "html.parser")
    
    # Run a loop to get all the reviews
    while True:
        # Get the div that has an id of "reviews"
        reviews = soup.find("div", {"id": "reviews"})
        
        # Get the class = list inside the reviews div
        reviews_list = reviews.find("div", {"class": "list"})
        
        # Get all the reviews
        for item in reviews_list:
            
            # Get all the text
            txt = item.get_text().strip().split("\n")
            
            # Remove white spaces
            txt = [x.strip() for x in txt]
            
            # If the name is empty, set it to "Anonymous"
            if txt[1] == '':
                txt[1] = "Anonymous"
            
            # Drop empty strings
            txt = [x for x in txt if x != '']
            
            # Create a dictionary to store the review
            review = {
                "Rating": txt[0],
                "Name": txt[1],
                "Location": txt[2],
                "Date": txt[3],
                "Service": txt[4],
                "Review": txt[5]
                }
            
            # Create a dataframe from the review
            row = pd.DataFrame(review, index=[0])
            
            # Concatenate the review to the review_data dataframe
            if review_data.empty:
                review_data = row
            else:
                review_data = pd.concat([review_data, row], ignore_index=True)
                
        # Get the next button that has class="page-next @px-1 @ml-1"
        next_button = driver.find_element(By.CLASS_NAME, "page-next")
        
        # If the next button is disabled, break the loop
        if next_button.get_attribute("disabled"):
            break
        
        # ActionChains(driver).move_to_element(next_button).perform()
        driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
        # Click the next button
        next_button.click()
        
        # Wait for the page to load
        time.sleep(2)
    
    # Sort the reviews by Rating and by Date
    review_data = review_data.sort_values(["Rating", "Date"], ascending=[False, False]).reset_index(drop=True)
    
    # Save the reviews to a csv file
    review_data.to_csv("assets/data/home_advisor_reviews.csv", index=False)


home_advisor_reviews(HOME_ADVISOR)

