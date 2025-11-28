import logging
import os
import time

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from telegram_notifier import TelegramNotifier

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

DEFAULT_WAIT_TIMEOUT = 20
BALANCE_XPATH = "/html/body/div[1]/div/div[2]/div/div/div/div/div[1]/section/div[1]/span/a/span"
CLAIM_BUTTON_XPATH = "/html/body/div[1]/div/div[2]/div/div/div/div/div[1]/section/div[2]/div[1]/div[2]/button"

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
PIXAI_TOKEN = os.getenv("PIXAI_TOKEN")
PIXAI_URL = os.getenv("PIXAI_URL")

if not all((BOT_TOKEN, CHAT_ID, PIXAI_TOKEN, PIXAI_URL)):
    raise RuntimeError("Missing required environment variables")

USE_DOCKER = os.getenv("USE_DOCKER_SELENIUM", "false").lower() == "true"
SELENIUM_REMOTE_URL = os.getenv("SELENIUM_REMOTE_URL")
CHROMEBINARY_PATH = os.getenv("CHROMEBINARY_PATH")
CHROMEDRIVER_PATH = os.getenv("CHROMEDRIVER_PATH")

if USE_DOCKER and not SELENIUM_REMOTE_URL:
    raise RuntimeError("SELENIUM_REMOTE_URL is required when USE_DOCKER is true")

if not USE_DOCKER and not all((CHROMEBINARY_PATH, CHROMEDRIVER_PATH)):
    raise RuntimeError("CHROMEBINARY_PATH and CHROMEDRIVER_PATH are required when USE_DOCKER is false")


def get_balance(driver: webdriver.Chrome) -> str:
    """
    Возвращает текст текущего баланса
    """

    return (
        WebDriverWait(driver, DEFAULT_WAIT_TIMEOUT)
        .until(ec.presence_of_element_located((By.XPATH, BALANCE_XPATH)))
        .text
    )


def claim_rewards(driver: webdriver.Chrome) -> bool:
    """
    Нажимает кнопку получения наград
    """

    button = WebDriverWait(driver, DEFAULT_WAIT_TIMEOUT).until(
        ec.presence_of_element_located((By.XPATH, CLAIM_BUTTON_XPATH))
    )
    time.sleep(10)

    if button.get_attribute("disabled") == "true":
        return False

    button.click()
    return True


def initialize_driver() -> webdriver.Chrome:
    """
    Создаёт и возвращает объект Chrome WebDriver
    """

    options = Options()
    options.add_argument("--window-size=1920,1200")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    )

    if USE_DOCKER:
        logger.info("Docker using detected")
        driver = webdriver.Remote(
            command_executor=SELENIUM_REMOTE_URL,
            options=options,
        )
    else:
        options.binary_location = CHROMEBINARY_PATH
        options.add_argument("--headless=new")
        service = Service(CHROMEDRIVER_PATH)
        driver = webdriver.Chrome(service=service, options=options)

    return driver


def main_logic(driver: webdriver.Chrome, tn: TelegramNotifier) -> None:
    """
    Основная логика получения ежедневной награды
    """

    logger.info("Opening URL (%s) and setting cookies...", PIXAI_URL)
    driver.get(PIXAI_URL)
    driver.add_cookie({"name": "user_token", "value": PIXAI_TOKEN, "path": "/"})
    driver.execute_script(
        "window.localStorage.setItem(arguments[0], arguments[1]);",
        "https://api.pixai.art:token",
        PIXAI_TOKEN,
    )
    driver.refresh()

    logger.info("Getting current balance...")
    current_balance = get_balance(driver)

    logger.info("Attempting to claim rewards...")
    is_claimed = claim_rewards(driver)
    if not is_claimed:
        logger.warning("Daily rewards is already claimed")
        tn.send_already_claimed_message(current_balance)
        return

    logger.info("Rewards claimed. Waiting for balance update...")
    time.sleep(5)

    new_balance = get_balance(driver)
    logger.info("Rewards claimed successfully. New balance: %s", new_balance)
    tn.send_successfully_claimed_message(new_balance)


def run() -> None:
    """
    Точка входа в программу
    """

    tn = TelegramNotifier(
        BOT_TOKEN,
        CHAT_ID,
        PIXAI_URL,
    )

    logger.info("Initializing driver...")
    driver = initialize_driver()
    logger.info("Driver initialized")

    try:
        main_logic(driver, tn)
    except Exception as e:
        logger.exception("Failed claiming daily rewards")
        tn.send_error_message(str(e))
    finally:
        driver.quit()


if __name__ == "__main__":
    run()
