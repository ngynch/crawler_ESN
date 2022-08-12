from typing import Dict
from bs4 import BeautifulSoup
from selenium import webdriver
import smtplib, ssl
import re
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import time
import configparser

def get_html_source(link:str) -> str:
    """get the html source code of a link

    Args:
        link (str): link to website

    Returns:
        str: html source code
    """
    driver = webdriver.Remote("http://chrome:4444/wd/hub", options=webdriver.ChromeOptions())
    driver.get(link)
    html = driver.page_source
    driver.quit()
    return html


def evaluate_html_esn(page_source: str) -> Dict[str,bool]:
    """evaluate which products are available, works only with ESN products

    Args:
        page_source (str): html source code

    Returns:
        Dict[str,bool]: dictionary with all products and whether they are available or not
    """
    products_available = {}
    soup = BeautifulSoup(page_source, 'html.parser')
    products = str(soup.find('div', {"class":"variant-input-wrap", "data-index":"option2"})).split("<option class=")[1:]
    
    #check if first element is available (website is bugged, even if its not available it is not disabled)
    first_elem_avail = str(soup.find('button', {"type":"submit", "name":"add"}))
    key = re.search(r'value="(.*)\"', products[0]).group(1)
    if "Out of stock" in first_elem_avail:
        products_available[key] = False
    else:
        products_available[key] = True

    for product in products[1:]:
        key = re.search(r'value="(.*)\"', product).group(1)
        products_available[key] = True if "disabled" not in product else False
    return products_available


def send_email(products: Dict[str, bool]):
    config = configparser.ConfigParser()
    config.read("config.ini")
    sender_email = config["EMAIL"]["account"]
    pw = config["EMAIL"]["password"]
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['Subject'] = "greif zu bruder"
    message = '\n'.join(str(products)[1:-1].split(', '))
    msg.attach(MIMEText(message))
    
    port = 465
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.mail.yahoo.com", port, context=context) as server:
        server.login(sender_email, pw)
        for receiver in config["EMAIL"]["receivers"].split(','):
            msg['To'] = receiver
            server.sendmail(sender_email, receiver, msg.as_string())
            print(f"Email sent to  {receiver} successfully")
            time.sleep(2)

def main():
    # link = "https://www.esn.com/en/products/esn-designer-whey"
    link = "https://www.esn.com/en/products/esn-isoclear-whey-isolate"
    html = get_html_source(link)
    products = evaluate_html_esn(html)
    if any(products.values()):
        send_email(products)
    else:
        print("No products available!")
if __name__ == "__main__":
    main()  
