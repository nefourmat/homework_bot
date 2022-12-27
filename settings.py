import os

from dotenv import load_dotenv

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
ALL_TOKENS_WAS_RECEIVED = 'Все токены успешно получены'
ABSENCE_ENVIRONMENT_VARIABLES = 'Отсутствие переменных окружения {}'
ERROR_ENVIRONMENT_VARIABLES = 'Ошибка переменных окружения'
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
    {exception}
    '''.strip()
WORK_STATUS_CHANGED = 'Изменился статус проверки работы "{}". {}'
TYPEERROR = 'Неверный формат данных,функ.вернула {}'
SUCCESSFUL_TELEGRAM_MESSAGE = 'Успешная отправка сообщения: {}'
FAILED_DECODE_IN_JSON = 'Не удалось раскодировать {} в json. Ошибка: {}'
ABSENCE_HW_KEY = 'В домашней работе нет ключа {}'
ABSENCE_HWORKS_KEY = "Отсутсвутет ключ 'homeworks'"
UNKNOW_HW_STATUS = 'Неизвестный статус домашки {}'
INVALIDJSON = 'Произошла ошибка JSON: {}'
NEW_CHECK_HW = 'Проверено новых домашек: {}'
LAST_FRONTIER_ERROR_MESSAGE = 'Сбой в работе программы: {}'
