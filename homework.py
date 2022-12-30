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
    TELEGRAM_TOKEN, TYPE_ERROR, UNKNOW_HOMEWORK_STATUS,
    WORK_STATUS_CHANGED, JSON_ERROR,
    FILED_SEND_MESSAGE, PRACTICUM_TOKEN
)


def check_tokens() -> bool:
    """Проверка токенов."""
    tokens = {
        'PRACTICUM_TOKEN': PRACTICUM_TOKEN,
        'TELEGRAM_TOKEN': TELEGRAM_TOKEN,
        'TELEGRAM_CHAT_ID': TELEGRAM_CHAT_ID
    }
    missing_tokens = [name for name, v in tokens.items() if not v]
    if missing_tokens:
        logging.critical(ABSENCE_ENVIRONMENT_VARIABLES.format(missing_tokens))
        raise InvalidTokens(ERROR_ENVIRONMENT_VARIABLES.format(missing_tokens))
    logging.debug(ALL_TOKENS_WAS_RECEIVED)


def send_message(bot, message) -> bool:
    """Отправляет сообщение в Telegram чат."""
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        logging.debug(SUCCESSFUL_TELEGRAM_MESSAGE.format(message))
        return True
    except Exception as error:
        logging.error(FILED_SEND_MESSAGE.format(message, error), exc_info=True)
        return False


def get_api_answer(timestamp) -> dict:
    """Делает запрос к эндпоинту API-сервиса."""
    request_data = {
        'url': ENDPOINT,
        'headers': HEADERS,
        'params': {'from_date': timestamp}
    }
    try:
        homework_statuses = requests.get(**request_data)
    except requests.RequestException as error:
        raise ConnectionError(
            REQUEST_ERROR_MESSAGE.format(
                exception=error, **request_data)
        )
    if homework_statuses.status_code != HTTPStatus.OK:
        raise InvalidResponseCode(
            REQUEST_ERROR_MESSAGE.format(
                error=homework_statuses.status_code, **request_data)
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
        raise TypeError(TYPE_ERROR.format(type(response)))
    if 'homeworks' not in response:
        raise KeyError(ABSENCE_HOMEWORKS_KEY)
    homeworks = response['homeworks']
    if not isinstance(homeworks, list):
        raise TypeError(TYPE_ERROR.format(type(homeworks)))
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
    current_status = homework['status']
    if current_status not in HOMEWORK_VERDICTS:
        raise ValueError(UNKNOW_HOMEWORK_STATUS.format(current_status))
    return WORK_STATUS_CHANGED.format(
        homework['homework_name'], HOMEWORK_VERDICTS.get(current_status)
    )


def main() -> None:
    """Основная логика работы бота."""
    check_tokens()
    logging.debug(check_tokens())
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    previous_error = ''
    while True:
        try:
            request = get_api_answer(timestamp)
            homeworks = check_response(request)
            if homeworks:
                homework_verdict = parse_status(homeworks[0])
                if send_message(bot=bot, message=homework_verdict):
                    timestamp = request.get('current_date', timestamp)
        except Exception as error:
            message = LAST_FRONTIER_ERROR_MESSAGE.format(error)
            logging.error(message)
            if str(previous_error) != error:
                if send_message(bot=bot, message=message):
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
