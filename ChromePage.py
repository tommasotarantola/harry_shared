import logging
import time
import random
from selenium.webdriver import Chrome
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

class ChromePage(Chrome):
    def __init__(self, driver_path):
        Chrome.__init__(self, driver_path)
        Chrome.maximize_window(self)

    # General scraping actions
    @staticmethod
    def cst_wait(mu=1, sd=0.5, min=0):
        wait_time = -1
        while wait_time <= min:
            wait_time = random.gauss(mu, sd)
        logging.debug("wait: {} secs".format(wait_time))
        time.sleep(wait_time)
        return True

    def cst_highlight(self, web_element):
        def apply_style(style):
            self.execute_script("arguments[0].setAttribute('style', arguments[1]);", web_element, style)
        original_style = web_element.get_attribute('style')
        apply_style("background: yellow; border: 2px solid blue;")
        time.sleep(1)
        apply_style(original_style)

    def cst_click(self, path, position=0, method="css"):
        self.cst_wait()
        try:
            elements = self.cst_find_elements(path, method)
            element = elements[position]

            element.click()

            logging.debug(f"clicking:\tpath:{path}")
            return True
        except Exception as error:
            logging.error(f"clicking:\t{path}\terror:{error}")
            return False

    def cst_write(self, text, path, position=0, method="css"):
        self.cst_wait()
        try:
            elements = self.cst_find_elements(path, method)
            element = elements[position]
            element.clear()

            element.send_keys(text)
            logging.debug(f"writing:\tpath:{path}\telement:{element.text}")
            return True
        except Exception as error:
            logging.error(f"writing:\tpath:{path}\terror:{error}")
            return False

    def cst_send_keys(self, key):
        action = ActionChains(self)
        action.send_keys(key)
        action.perform()

    # General scraping utilities
    def cst_find_elements(self, path, method = "css", delay=5, log=False):
        try:
            if method == "css":
                elements = WebDriverWait(self, delay).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, path)))
            elif method == "xpath":
                elements = WebDriverWait(self, delay).until(
                    EC.presence_of_all_elements_located((By.XPATH, path)))
            elif method == "class":
                elements = WebDriverWait(self, delay).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, path)))
            else:
                raise Exception("invalid cst_find_elements method")
            # for extensive log
            if log:
                logging.debug(f"finding:\tpath{path}\tmethod:{method}")
            # for NoneType error
            if elements is None:
                raise Exception ("element not found")

            return elements
        except Exception as error:
            if log:
                logging.error("path: {} \terror: {}".format(path, error))

    def cst_load_retrieve_parse(self, path, method = "css", max_attempts=3, until=None,
                                parse_function=None, scroll_method = "page"):
        objects = []
        useless_attempt = 0
        while useless_attempt <= max_attempts:
            self.cst_wait()
            found_something = False

            visible_elements = self.cst_find_elements(path, method)

            for visible_element in visible_elements:
                if parse_function is None:
                    obj = visible_element
                else:
                    obj = parse_function(visible_element)
                if obj not in objects:
                    objects.append(obj)
                    found_something = True
                    useless_attempt = 0
                    if until is not None:
                        if len(objects) >= until:
                            return objects

            if not found_something:
                useless_attempt += 1
            if scroll_method == "page":
                self.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            elif scroll_method == "web_element":
                visible_elements[-1].send_keys(Keys.PAGE_DOWN)
            else:
                raise Exception("Invalid method")
        return objects
