# Домашнее задание по теме "Клавиатура кнопок".
# ВНИМАНИЕ: Данный код разработан в учебных целях, комментарии добавлены для себя!!!

from aiogram import Bot, Dispatcher, types
# Импортируем основные классы и типы из библиотеки aiogram, необходимые для создания ботов
from aiogram.contrib.fsm_storage.memory import MemoryStorage
# Импортируем класс MemoryStorage для хранения состояния пользователей в памяти (используется для машинных состояний)
from aiogram.dispatcher import FSMContext
# Импортируем контекст FSMContext для работы с машинами состояний
from aiogram.dispatcher.filters.state import State, StatesGroup
# Импортируем классы State и StatesGroup для определения различных состояний машины состояний
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton # Импортируем классы для создания клавиатур и кнопок

from aiogram.utils import executor # Импортируем функцию executor для запуска длинного поллинга бота


api = ""  # Определяем переменную api, которая хранит токен Telegram-бота

bot = Bot(token=api) # Создаем экземпляр класса Bot, передавая ему токен для авторизации
storage = MemoryStorage() # Создаем экземпляр класса MemoryStorage для хранения состояний пользователей
dp = Dispatcher(bot, storage=storage)
# Создаем диспетчер для управления сообщениями и состояниями, привязывая его к нашему боту и хранилищу состояний

# Создаем клавиатуру с двумя кнопками
keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
# Создаем объект клавиатуры с возможностью адаптации размера под устройство пользователя
buttons = [
    KeyboardButton('Рассчитать'),  # Первая кнопка на клавиатуре
    KeyboardButton('Информация')  # Вторая кнопка на клавиатуре
]
keyboard.add(*buttons)

# Добавляем обе кнопки на клавиатуру

class UserState(StatesGroup):  # Класс для описания возможных состояний пользователя
    age = State()  # Состояние для ввода возраста
    growth = State()  # Состояние для ввода роста
    weight = State()  # Состояние для ввода веса

@dp.message_handler(commands=['start'])  # Декорируем функцию как обработчик команд '/start'
async def start_message(message: types.Message):
    await message.answer('Привет! Я бот, помогающий твоему здоровью.', reply_markup=keyboard)
    # Отправляем приветственное сообщение с прикрепленной клавиатурой


@dp.message_handler(lambda message: message.text == 'Рассчитать')  # Обрабатываем нажатие кнопки 'Рассчитать'
async def set_age(message: types.Message):
    await message.answer('Введите свой возраст:')  # Запрашиваем ввод возраста
    await UserState.age.set()  # Устанавливаем состояние для ввода возраста

@dp.message_handler()  # Обрабатываем все остальные сообщения
async def all_message(message):
    await message.answer("Введите команду /start, чтобы начать общение.")  # Просим ввести команду '/start'

@dp.message_handler(state=UserState.age)  # Обрабатываем сообщения в состоянии 'возраст'
async def set_growth(message: types.Message, state: FSMContext):
    await state.update_data(age=int(message.text))  # Сохраняем введенный возраст в контексте состояния
    await message.answer('Введите свой рост:')  # Запрашиваем ввод роста
    await UserState.next()  # Переходим к следующему состоянию (рост)

@dp.message_handler(state=UserState.growth)  # Обрабатываем сообщения в состоянии 'рост'
async def set_weight(message: types.Message, state: FSMContext):
    await state.update_data(growth=float(message.text))  # Сохраняем введенный рост в контексте состояния
    await message.answer('Введите свой вес:')  # Запрашиваем ввод веса
    await UserState.next()  # Переходим к следующему состоянию (вес)

@dp.message_handler(state=UserState.weight)  # Обрабатываем сообщения в состоянии 'вес'
async def send_calories(message: types.Message, state: FSMContext):
    await state.update_data(weight=float(message.text))  # Сохраняем введенный вес в контексте состояния

    user_data = await state.get_data()  # Получаем все сохраненные данные
    age = user_data['age']  # Извлекаем возраст
    growth = user_data['growth']  # Извлекаем рост
    weight = user_data['weight']  # Извлекаем вес

    calories_norm = 10 * weight + 6.25 * growth - 5 * age + 5  # Рассчитываем норму калорий

    await message.answer(f"Ваша норма калорий: {calories_norm:.2f}")  # Выводим результат расчета

    await state.finish()  # Завершаем работу с машиной состояний


if __name__ == '__main__':  # Проверка, является ли данный файл точкой входа приложения
    executor.start_polling(dp, skip_updates=True)  # Запускаем бесконечный цикл опроса обновлений от Telegram