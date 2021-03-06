import requests
from selenium import webdriver
import selenium as se
from selenium.common.exceptions import NoSuchElementException
import time
from time import sleep
from random import randint
from decimal import Decimal

post_params = {'bot_id': 'your_bot_ID',
               'text': "Starting Uniqlo bot"}
requests.post('https://api.groupme.com/v3/bots/post', params=post_params)

options = se.webdriver.ChromeOptions()

# chrome is set to headless
options.add_argument('headless')

driver = se.webdriver.Chrome(options=options)

# The Uniqlo product you want to track
driver.get("https://www.uniqlo.com/us/en/men/sale")

# global list for items that have already gotton a message
sent_list = []


def check_exists_by_xpath(xpath, item):
    try:
        item.find_element_by_xpath(xpath)
    except NoSuchElementException:
        return False
    return True


def check_for_price(class_name, sale_price_path, standard_price_path, item_name_path):
    try:
        driver.refresh
        # gets all products and calls each of them item
        for item in driver.find_elements_by_class_name(class_name):
            # checking if the spans exists so there arn't any errors when weird stuff happens
            if check_exists_by_xpath(standard_price_path, item) == True and check_exists_by_xpath(sale_price_path, item) == True:
                product_standard_price = item.find_element_by_xpath(
                    standard_price_path).text
                product_sale_price = item.find_element_by_xpath(
                    sale_price_path).text
            else:
                # sets prices to make sure it gets printed out (better to be safe then sorry)
                product_standard_price = "$1000.00"
                product_sale_price = "$1.01"

            # product string format is in $__.__ so we use [1:] to get rid of $
            sale_percent = float(
                product_sale_price[1:]) / float(product_standard_price[1:])

            # 1-.05 is the min amount of sale there has to be
            if sale_percent < .26 and item.id not in sent_list:
                item_name = item.find_element_by_xpath(item_name_path).text
                # print for debugging
                print(
                    f"{item_name} ON SALE for {product_sale_price} at {round((1-sale_percent)*100,2)}% off")
                post_params = {'bot_id': 'your_bot_ID',
                               'text': f"{item_name} ON SALE for {product_sale_price} at {round((1-sale_percent)*100,2)}% off"}
                requests.post(
                    'https://api.groupme.com/v3/bots/post', params=post_params)
                # adds id to sent list so the message isn't sent mutiple times
                sent_list.append(item.id)

    except requests.exceptions.RequestException as e:
        # Sends an error message and waits another 60 seconds
        post_params = {'bot_id': 'your_bot_ID',
                       'text': "exception " + str(e)}
        requests.post('https://api.groupme.com/v3/bots/post',
                      params=post_params)
        sleep(60)
    return False


while True:
    class_name = 'product-tile'
    sale_price_path = ".//span[@class='product-sales-price']"
    standard_price_path = ".//span[@class='product-standard-price']"
    item_name_path = ".//a[@class='name-link']"
    # calls function every 30-60 seconds
    current_state = check_for_price(
        class_name, sale_price_path, standard_price_path, item_name_path)
    sleep(randint(30, 60))
