import json
import time
from typing import Dict, List, Union
import logging

from selenium.webdriver import Chrome
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located
from selenium.webdriver.support.select import By

FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('Selenium app')
logger.setLevel(logging.INFO)


def actions() -> Union[Dict[str, List[Dict[str, any]]], None]:
    """
    Returns all the actions stored in json.

    :return: actions array
    """
    
    try:
        with open("./actions.json", 'r') as actions_file:
            actions_data = actions_file.read()
            user_actions: Dict[str, List[Dict[str, any]]] = json.loads(actions_data)
            return user_actions
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        logger.error('Error reading file. Probably file does not exist or the format is wrong.')
        return None


def reset_mouse_position(driver, x_offset: int, y_offset: int):
    """
    Resets mouse position in browser to prevent out of bound error.

    :param x_offset:
    :param y_offset:
    :param driver: Selenium webdriver
    :return: None
    """

    action_chain = ActionChains(driver)
    action_chain.move_by_offset(-x_offset, -y_offset).perform()
    logger.info(f"Mouse position reset by: {x_offset}, {y_offset}")


def execute_actions(driver, wait, user_actions: Dict[str, List[Dict[str, any]]]):
    """
    Executes all the actions in a browser.

    :param driver: Selenium webdriver
    :param wait: Selenium wait object
    :param user_actions:
    :return: None
    """

    try:
        wait.until(presence_of_element_located((By.TAG_NAME, 'body')))
        time.sleep(5)

        prev_x_offset: Union[int, None] = None
        prev_y_offset: Union[int, None] = None
        prev_scroll = 0
        for action in user_actions["user_actions"]:
            event: str = action["event"]
            data: Union[str, Dict[str, Union[int, str]]] = action["data"]

            action_chain = ActionChains(driver)

            if event == "click":
                if prev_x_offset is not None and prev_y_offset is not None:
                    reset_mouse_position(driver=driver, x_offset=prev_x_offset, y_offset=prev_y_offset)

                x_offset: int = data["xOffset"]
                y_offset: int = data["yOffset"]

                action_chain.move_by_offset(x_offset, y_offset).click().perform()
                logger.info(f"Clicked at: {x_offset}, {y_offset}")

                prev_x_offset = x_offset
                prev_y_offset = y_offset

            elif event == "keyPress":
                key = data
                action_chain.send_keys(key).perform()
                logger.info(f"Key pressed: {key}")

            elif event == "scroll":
                # TODO: Handle horizontal scroll
                scroll_height: int = data["yOffset"]
                driver.execute_script(f"window.scrollBy(0, {scroll_height - prev_scroll})")
                logger.info(f"Vertical scroll by: {scroll_height}")
                
                prev_scroll = scroll_height

            time.sleep(0.5)
    except Exception as err:
        logger.error(str(err))


if __name__ == "__main__":
    URL: str = input('Enter the URL of your webpage: ')

    driver = Chrome()
    wait = WebDriverWait(driver, 10)

    driver.get(url=URL)
    driver.maximize_window()

    actions: Union[Dict[str, List[Dict[str, any]]], None] = actions()

    if actions:
        execute_actions(driver=driver, wait=wait, user_actions=actions)
