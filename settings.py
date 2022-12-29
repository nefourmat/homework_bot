import os

from dotenv import load_dotenv

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
ALL_TOKENS_WAS_RECEIVED = 'Все токены успешно получены'
ABSENCE_ENVIRONMENT_VARIABLES = '''
    Отсутствие переменных окружения.
    Пробущен токен: {missing_token}
'''

ERROR_ENVIRONMENT_VARIABLES = 'Ошибка переменных окружения {}'
RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}
REQUEST_ERROR_MESSAGE = '''
    Получить ответ от Практикума не удалось.
    {url}
    Заголовок запроса: {headers}
    Параметры запроса: {params}
    Код статуса: {error}
    '''.strip()
WORK_STATUS_CHANGED = 'Изменился статус проверки работы "{}". {}'
TYPE_ERROR = 'Неверный формат данных,функ.вернула {}'
SUCCESSFUL_TELEGRAM_MESSAGE = 'Успешная отправка сообщения: "{}"'
FAILED_DECODE_IN_JSON = 'Не удалось раскодировать {} в json. Ошибка: {}'
ABSENCE_HOMEWORK_KEY = 'В домашней работе нет ключа {}'
ABSENCE_HOMEWORKS_KEY = "Отсутсвутет ключ 'homeworks'"
UNKNOW_HOMEWORK_STATUS = 'Неизвестный статус домашки {}'
INVALIDJSON = 'Произошла ошибка JSON: {}'
NEW_CHECK_HOMEWORK = 'Проверено новых домашек: {}'
LAST_FRONTIER_ERROR_MESSAGE = 'Сбой в работе программы: {}'
TOKENS = (
    ('PRACTICUM_TOKEN', PRACTICUM_TOKEN),
    ('TELEGRAM_TOKEN', TELEGRAM_TOKEN),
    ('TELEGRAM_CHAT_ID', TELEGRAM_CHAT_ID),
)
JSON_ERROR = '''
    'Ошибка в json: {error}
    Ключ: {key}
    Адрес: {url}
    Заголовок запроса: {headers}
    Параметры запроса: {params}'
    '''
FILED_SEND_MESSAGE = 'Не удалось отправить сообщение"{}" ошибка "{}"'
