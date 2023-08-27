# Webcrawler

# importing required libraries

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from concurrent.futures import ThreadPoolExecutor
import time
import pandas as pd
from selenium.webdriver.support.ui import Select
import requests
from lxml import html



# Measure time taken to scrape the website
start_time = time.time()

# Initialize a Chrome webdriver to work with the AJAX
driver = webdriver.Chrome()
driver.maximize_window()
options = webdriver.ChromeOptions()
options.add_experimental_option("detach", True)

website = 'https://www.cermati.com/karir/lowongan'
driver.get(website)


# Crawler function to scrape out the necessary data using LXML library
def crawler(url):
    response = requests.get(url)
    tree = html.fromstring(response.content)
    t = tree.xpath('//*[@class="job-title"]/text()')[0]
    title.append(t)
    l = tree.xpath('//spl-job-location/@formattedaddress')[0]
    location.append(l)
    des = tree.xpath('//section[@id="st-jobDescription"]//li/text()')
    # removing '\u00a0' with ' '
    new_des = [s.replace('\u00a0', ' ') for s in des]
    new_des = [s.replace('\u2019', ' ') for s in new_des]
    description.append(new_des)
    qual = tree.xpath('//section[@id="st-qualifications"]//li/text()')
    new_qual = [s.replace('\u00a0', ' ') for s in des]
    new_qual = [s.replace('\u2019', ' ') for s in new_qual]
    qualification.append(new_qual)
    type = tree.xpath('//*[@class="job-detail"]/text()')[0]
    job_type.append(type)


# initialize a empty dictionary to store the final results

jobs_byDept = {}

# find the Dropdown to select the Jobs by their Departments
dropdown = driver.find_element(By.XPATH, '//select[@id="job-department"]')
select = Select(dropdown)
options = select.options

# looping through the each options to select individual Departments
for option in options[1:]:
    # Variable to store necessary columns
    department = option.text
    title = []
    location = []
    description = []
    qualification = []
    job_type = []
    # can't able to find the Posted by person name on the website
    # postedBy = []

    # selecting the option by using 'select_by_visible_text' method
    select.select_by_visible_text(option.text)

    # putting the browser to halt for 1 second to AJAX to complete
    time.sleep(1)

    # Using while loop for the continous looping
    while True:
        try:
            # using WebDriverWait and expected_conditions to wait for the page to load until the elment found
            element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, '//*[@class="page-job-wrapper"]'))
            )

            # collecting urls from the href attribute
            links = [a.get_attribute('href') for a in
                     driver.find_elements(By.XPATH, '//*[@class="page-job-list-wrapper"]/a[1]')]

            # Initializing a Parallel operation by assigning 4 worker threads
            with ThreadPoolExecutor(max_workers=4) as executor:
                executor.map(crawler, links)

        except:
            break

        # Trying to find the 'next_button' was enabled in the page for pagination
        try:
            next_button = driver.find_element(By.XPATH, '//i[@class="fa fa-angle-right"]/..')
            if next_button.get_attribute("disabled") == "true":
                break
            next_button.click()
            time.sleep(2)

        except:
            break

    # Converting the list of objects into pandas Dataframe
    df = pd.DataFrame(
        {'title': title, 'location': location, 'description': description, 'qualification': qualification,
         'job_type': job_type})
    # covert to dictionary
    data = df.to_dict("records")
    result = {department: data}
    jobs_byDept.update(result)
driver.quit()

# write to dictionary to the json file
with open('solution.json', 'w') as f:
    pd.json_normalize(jobs_byDept).to_json(f, orient='records')
end_time = time.time()
duration = round(end_time - start_time, 3)
print(f'The time taken to complete {duration}s.')
print("Website scraped successfully and the output was saved to 'solution.json'!!!")
