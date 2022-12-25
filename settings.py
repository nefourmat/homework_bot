import os

from dotenv import load_dotenv

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
KEYERROR = 'Ошибка. Нет ключа {exception}'
ALL_TOKENS_WAS_RECEIVED = 'Все токены успешно получены'
ABSENCE_ENVIRONMENT_VARIABLES = 'Отсутствие обязательных переменных окружения'
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
