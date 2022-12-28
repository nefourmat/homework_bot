import logging
import time
from http import HTTPStatus

import requests
import telegram

from exceptions import (
    InvalidTokens, ResponseErrorException,
    InvalidResponseCode
)
from settings import (
    ABSENCE_ENVIRONMENT_VARIABLES, ABSENCE_HOMEWORK_KEY,
    ABSENCE_HOMEWORKS_KEY, ALL_TOKENS_WAS_RECEIVED, ENDPOINT,
    ERROR_ENVIRONMENT_VARIABLES,
    HEADERS, HOMEWORK_VERDICTS,
    LAST_FRONTIER_ERROR_MESSAGE, NEW_CHECK_HOMEWORK,
    REQUEST_ERROR_MESSAGE, RETRY_PERIOD,
    SUCCESSFUL_TELEGRAM_MESSAGE, TELEGRAM_CHAT_ID,
    TELEGRAM_TOKEN, TYPEERROR, UNKNOW_HW_STATUS,
    WORK_STATUS_CHANGED, JSON_ERROR,
    FILED_SEND_MESSAGE, PRACTICUM_TOKEN
)
TOKENS = (
    ('PRACTICUM_TOKEN', PRACTICUM_TOKEN),
    ('TELEGRAM_TOKEN', TELEGRAM_TOKEN),
    ('TELEGRAM_CHAT_ID', TELEGRAM_CHAT_ID),
)
T = (PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID)


def check_tokens() -> bool:
    """Проверка токенов."""
    for value in (PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID):
        if not value:
            logging.critical(
                ABSENCE_ENVIRONMENT_VARIABLES
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
        logging.error(FILED_SEND_MESSAGE.format(message, error), exc_info=True)


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
            raise InvalidResponseCode(
                REQUEST_ERROR_MESSAGE.format(
                    error=homework_statuses.status_code, **request_data)
            )
    #  тесты не пропускают без RequestException
    except requests.RequestException as error:
        raise ConnectionError(
            REQUEST_ERROR_MESSAGE.format(
                exception=error, **request_data)
        )
    homeworks_json = homework_statuses.json()
    for key in ['error', 'code']:
        if key in homeworks_json:
            logging.debug(homeworks_json[key])
            raise ResponseErrorException(
                JSON_ERROR.format
                (error=homeworks_json[key], key=key, **request_data))
    return homeworks_json


def check_response(response) -> list:
    """Проверка ответ API на соответствие."""
    if not isinstance(response, dict):
        raise TypeError(TYPEERROR.format(type(response)))
    if 'homeworks' not in response:
        raise KeyError(ABSENCE_HOMEWORKS_KEY)
    homeworks = response.get('homeworks')
    if not isinstance(homeworks, list):
        raise TypeError(TYPEERROR.format(type(homeworks)))
    logging.debug(NEW_CHECK_HOMEWORK.format(len(homeworks)))
    return homeworks


def parse_status(homework) -> str:
    """Провека статуса ДЗ."""
    homework_keys = [
        'homework_name',
        'status'
    ]
    for key in homework_keys:
        if key not in homework:
            raise KeyError(ABSENCE_HOMEWORK_KEY.format(key))
    homework_name = homework.get('homework_name')
    current_status = homework.get('status')
    if current_status not in HOMEWORK_VERDICTS:
        raise ValueError(UNKNOW_HW_STATUS.format(current_status))
    return WORK_STATUS_CHANGED.format(
        homework_name, HOMEWORK_VERDICTS.get(homework.get('status'))
    )


def main() -> None:
    """Основная логика работы бота."""
    check_tokens()
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    previous_error = ''
    while True:
        try:
            request = get_api_answer(timestamp)
            homeworks = check_response(request)
            if homeworks:
                homework_verdict = parse_status(homeworks[0])
                send_message(bot=bot, message=homework_verdict)
                timestamp = request.get('current_date', timestamp)
        except Exception as error:
            message = LAST_FRONTIER_ERROR_MESSAGE.format(error)
            logging.error(message)
            if str(previous_error) != str(error):
                send_message(bot=bot, message=message)
                previous_error = error
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        format=(
            '%(asctime)s [%(levelname)s] | '
            '%(funcName)s:%(lineno)d | %(message)s'
        ),
        handlers=[
            logging.FileHandler(
                __file__ + '.log', mode='w', encoding='UTF-8',
            ),
            logging.StreamHandler()],
    )
    logging.getLogger('urllib3').setLevel('CRITICAL')
    main()
