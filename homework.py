import logging
import sys
import time
from http import HTTPStatus

import requests
import telegram

from exceptions import InvalidTokens
from settings import (ABSENCE_ENVIRONMENT_VARIABLES, ABSENCE_HW_KEY,
                      ABSENCE_HWORKS_KEY, ALL_TOKENS_WAS_RECEIVED, ENDPOINT,
                      ERROR_ENVIRONMENT_VARIABLES, FAILED_DECODE_IN_JSON,
                      HEADERS, HOMEWORK_VERDICTS, INVALIDJSON,
                      LAST_FRONTIER_ERROR_MESSAGE, NEW_CHECK_HW,
                      PRACTICUM_TOKEN, REQUEST_ERROR_MESSAGE, RETRY_PERIOD,
                      SUCCESSFUL_TELEGRAM_MESSAGE, TELEGRAM_CHAT_ID,
                      TELEGRAM_TOKEN, TYPEERROR, UNKNOW_HW_STATUS,
                      WORK_STATUS_CHANGED)


def check_tokens() -> bool:
    """Проверка токенов."""
    tokens = (
        ('PRACTICUM_TOKEN', PRACTICUM_TOKEN),
        ('TELEGRAM_TOKEN', TELEGRAM_TOKEN),
        ('TELEGRAM_CHAT_ID', TELEGRAM_CHAT_ID),
    )
    for token, value in tokens:
        if not value:
            logging.critical(
                ABSENCE_ENVIRONMENT_VARIABLES.format(token)
            )
            raise InvalidTokens(ERROR_ENVIRONMENT_VARIABLES)
    logging.debug(ALL_TOKENS_WAS_RECEIVED)
    return True


def send_message(bot, message) -> None:
    """Отправляет сообщение в Telegram чат."""
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        logging.debug(SUCCESSFUL_TELEGRAM_MESSAGE.format(message))
    except Exception as error:
        logging.error(error, exc_info=True)


def get_api_answer(timestamp) -> dict:
    """Делает запрос к эндпоинту API-сервиса."""
    request_data = {
        'url': ENDPOINT,
        'headers': HEADERS,
        'params': {'from_date': timestamp}
    }
    try:
        homework_statuses = requests.get(**request_data)
        if homework_statuses.status_code != HTTPStatus.OK:
            raise requests.exceptions.HTTPError(
                f'Ошибка. Статус код: {homework_statuses.status_code}')
    except requests.RequestException as error:
        raise ConnectionError(
            REQUEST_ERROR_MESSAGE.format(
                exception=error, **request_data)
        )
    try:
        homeworks_json = homework_statuses.json()
    except requests.JSONDecodeError as e:
        raise ConnectionError(
            FAILED_DECODE_IN_JSON.format(homework_statuses, e))
    return homeworks_json


def check_response(response) -> list:
    """Проверка ответ API на соответствие."""
    if not isinstance(response, dict):
        raise TypeError(TYPEERROR.format(type(response)))
    if 'homeworks' not in response:
        raise KeyError(ABSENCE_HWORKS_KEY)
    homeworks = response.get('homeworks')
    if not isinstance(homeworks, list):
        raise TypeError(TYPEERROR.format(type(response)))
    logging.debug(NEW_CHECK_HW.format(len(homeworks)))
    return homeworks


def parse_status(homework) -> str:
    """Провека статуса ДЗ."""
    homework_keys = [
        'homework_name',
        'status'
    ]
    for key in homework_keys:
        if key not in homework:
            raise KeyError(ABSENCE_HW_KEY.format(key))
    homework_name = homework.get('homework_name')
    current_status = homework.get('status')
    if current_status not in HOMEWORK_VERDICTS:
        raise KeyError(UNKNOW_HW_STATUS.format(current_status))
    if current_status is None:
        raise requests.exceptions.InvalidJSONError(INVALIDJSON)
    verdict = HOMEWORK_VERDICTS.get(homework.get('status'))
    return WORK_STATUS_CHANGED.format(homework_name, verdict)


def main() -> None:
    """Основная логика работы бота.
    Обрабаываем исключения, при повторном одинаковой ошибки мы сообщение
    не отправляем
    """
    if not check_tokens():
        sys.exit(ERROR_ENVIRONMENT_VARIABLES)
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    previous_error = None
    while True:
        try:
            request = get_api_answer(timestamp)
            timestamp = request.get('current_date')
            get_homeworks = check_response(request)
            if get_homeworks:
                homework_verdict = parse_status(get_homeworks[0])
                send_message(bot=bot, message=homework_verdict)
        except Exception as error:
            message = LAST_FRONTIER_ERROR_MESSAGE.format(error)
            if not isinstance(previous_error, type(error)):
                send_message(bot=bot, message=message)
                logging.error(message)
            previous_error = error
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        filename=__file__ + '.log',
        format=(
            '%(asctime)s [%(levelname)s] | '
            '%(funcName)s:%(lineno)d | %(message)s'
        ),
        encoding='UTF-8',
        filemode='w'
    )
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '[%(levelname)s] | %(funcName)s:%(lineno)d | %(message)s')
    console_handler.setFormatter(formatter)
    logging.getLogger('').addHandler(console_handler)
    logger = logging.getLogger(__name__)
    logging.getLogger('urllib3').setLevel('CRITICAL')
    main()
