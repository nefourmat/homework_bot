import logging
import sys
import time
from http import HTTPStatus

import requests
import telegram

from settings import (ABSENCE_ENVIRONMENT_VARIABLES, ALL_TOKENS_WAS_RECEIVED,
                      ENDPOINT, HEADERS, HOMEWORK_VERDICTS, PRACTICUM_TOKEN,
                      REQUEST_ERROR_MESSAGE, RETRY_PERIOD, TELEGRAM_CHAT_ID,
                      TELEGRAM_TOKEN, KEYERROR)


def check_tokens():
    """Проверка токенов."""
    if all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]):
        logging.debug(ALL_TOKENS_WAS_RECEIVED)
        return True
    logging.critical(ABSENCE_ENVIRONMENT_VARIABLES)
    raise Exception(ABSENCE_ENVIRONMENT_VARIABLES)


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        logging.debug('Успешная отправка сообщения в Телеграм')
    except Exception:
        logging.error('Ошибка отправки сообщения в Телеграм')


def get_api_answer(timestamp):
    """Делает запрос к эндпоинту API-сервиса."""
    request_data = {
        'url': ENDPOINT,
        'headers': HEADERS,
        'params': {'from_date': timestamp}
    }
    try:
        homework_statuses = requests.get(**request_data)
    except requests.RequestException as error:
        logging.error(
            REQUEST_ERROR_MESSAGE.format(exception=error, **request_data))
        raise ConnectionError(
            REQUEST_ERROR_MESSAGE.format(
                exception=error, **request_data)
        )
    if homework_statuses.status_code != HTTPStatus.OK:
        logging.error(f'Ошибка. Статус код: {homework_statuses.status_code}')
        raise Exception(f'Ошибка. Статус код: {homework_statuses.status_code}')
    logging.debug(f'Функция вернула json {homework_statuses.json()}')
    return homework_statuses.json()


def check_response(response):
    """Проверка ответ API на соответствие."""
    if not isinstance(response, dict):
        raise TypeError('Неверный формат данных, ожидаем словарь')
    homework = response.get('homeworks')
    if not isinstance(homework, list):
        raise TypeError('Неверный формат homeworks, ожидаем список')
    return homework[0]


def parse_status(homework):
    """Провека статуса ДЗ."""
    homework_name = homework.get('homework_name')
    if not homework_name:
        raise KeyError('В домашней работе нет ключа homework_name')
    current_status = homework.get('status')
    if (current_status not in HOMEWORK_VERDICTS) or (current_status is None):
        raise KeyError(KEYERROR.format(exception=current_status))
    verdict = HOMEWORK_VERDICTS.get(homework.get('status'))
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота.
    Обрабаываем исключения, при повторном одинаковой ошибки мы сообщение
    не отправляем
    """
    logging.info('Запущенна функция main')
    check_tokens()
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    while True:
        try:
            request = get_api_answer(timestamp)
            homework = check_response(request)
            homework_verdict = parse_status(homework)
            send_message(bot=bot, message=homework_verdict)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.error(message)
        finally:
            logging.debug('Таймер сработал')
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
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    logger.addHandler(handler)
    logging.getLogger('urllib3').setLevel('CRITICAL')
    main()
