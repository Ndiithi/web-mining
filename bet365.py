import logging
from time import sleep
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
import csv

start_url='https://www.bet365.com.au/en/'

class Bet365:
    
    def __init__(self):
        self.driver = webdriver.Firefox()
        
        
    def open_url(self,url):
        self.driver.get(url)
        try:
            enter_site_link = WebDriverWait(self.driver, 10).until(lambda x: x.find_element_by_css_selector("a#TopPromotionBetNow"))
            sleep(5)
            enter_site_link.click()
        except NoSuchElementException,e:
            logger.info(e)
        
        
    def parse_page(self,web_page=None):
            try:
                logger.info("Parsing category menu")
                category_list=WebDriverWait(self.driver, 100).until(lambda x: x.find_elements_by_css_selector("div.wn-Classification"))
                for menu in category_list:
                    if(menu.text=='Soccer'):
                        sleep(5)
                        menu.click()
                        break
                elite_euro_list=WebDriverWait(self.driver, 100).until(lambda x: x.find_elements_by_css_selector("div.sm-CouponLink div.sm-CouponLink_Label "))
                for elem in elite_euro_list:
                    if(elem.text=='Elite Euro List'):
                        sleep(5)
                        elem.click()
                        break
                with open("persons.csv","wb") as csvfile:
                    filewriter = csv.writer(csvfile, delimiter=',',
                                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
                    filewriter.writerow(['Name', 'Profession'])
                    filewriter.writerow(['Derek', 'Software Developer'])
                    filewriter.writerow(['Steve', 'Software Developer'])
                    filewriter.writerow(['Paul', 'Manager'])
                    print('File writting done')
            except Exception,e:
                logger.info(e)
    
    
    def tear_down(self):
        logger.info("terminating Bet365 crawler, shutting down web driver")
        self.driver.quit()

if __name__== "__main__":
    logging.basicConfig(filename='/tmp/bet365.log', filemode='w', level=logging.DEBUG, format='%(asctime)s %(message)s')
    logger = logging.getLogger(__name__)
    logger.info("Crawler started")
    bet365=Bet365()
    try:
        bet365.open_url(start_url)
        bet365.parse_page()
        sleep(5)
    except Exception as e:
        print(e)
        logger.error(e, exc_info=True)
    finally:
        bet365.tear_down()
        
        