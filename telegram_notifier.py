import logging
import time

from telebot import TeleBot

logger = logging.getLogger(__name__)


class TelegramNotifier:
    _BASE_MESSAGE = "\n≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡\nТекущий баланс: <b>{} ⧈</b>\nПрофиль: {}"
    _ALREADY_CLAIMED_MESSAGE = (
        "🟠 <b>Не удалось</b> забрать <b>ежедневные</b> награды. "
        "Бонус за <b>сегодня</b> уже был <b>собран</b>." + _BASE_MESSAGE
    )
    _SUCCESSFULLY_CLAIMED_MESSAGE = "🟢 Ежедневные <b>награды</b> успешно <b>собраны</b>." + _BASE_MESSAGE
    _ERROR_MESSAGE = (
        "🔴 Произошла <b>ошибка</b> при получении ежедневных <b>наград</b>:\n<code>{}</code>"
        "\n≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡\nПрофиль: {}"
    )

    def __init__(self, token: str, chat_id: str, url: str) -> None:
        self._bot = TeleBot(token, parse_mode="html")
        self._chat_id = chat_id
        self._url = url

    def _send_message(self, message: str) -> None:
        for attempt in range(3):
            logger.info("Send notification (attempt №%s)...", attempt + 1)
            try:
                self._bot.send_message(self._chat_id, message)
                logger.info("Notification successfully sent")
                break
            except Exception:
                logger.exception("Failed to send notification")
                if attempt < 2:
                    logger.info("Waiting for 10 seconds...")
                    time.sleep(10)

    def send_already_claimed_message(self, balance: str) -> None:
        message = self._ALREADY_CLAIMED_MESSAGE.format(balance, self._url)
        self._send_message(message)

    def send_successfully_claimed_message(self, new_balance: str) -> None:
        message = self._SUCCESSFULLY_CLAIMED_MESSAGE.format(new_balance, self._url)
        self._send_message(message)

    def send_error_message(self, error: str) -> None:
        message = self._ERROR_MESSAGE.format(error, self._url)
        self._send_message(message)
