import os
import ccxt
import asyncio
import numpy as np
import pandas as pd
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

# 🔹 Настройки
API_TOKEN = os.getenv("8153754798:AAGY5YkGcq9iNc_bhF62Q73wSJgv8aO7ZRk")  # Переменные окружения должны быть правильными
CHAT_ID = os.getenv("178010516")  # ID чата
SYMBOL = "BTC/USDT"  # Валютная пара
EXCHANGE_NAME = "binance"  # Биржа
MA_SHORT = 7  # Короткая скользящая средняя
MA_LONG = 25  # Длинная скользящая средняя
TIMEFRAME = "1h"  # Таймфрейм (1h = 1 час)

# 🔹 Подключаем Telegram-бота
bot = Bot(token=API_TOKEN, parse_mode=ParseMode.MARKDOWN)
dp = Dispatcher()

# 🔹 Подключаемся к бирже
exchange = getattr(ccxt, EXCHANGE_NAME)({'rateLimit': 1200})

async def get_signal():
    """Проверка пересечения скользящих средних и отправка сигналов"""
    try:
        candles = exchange.fetch_ohlcv(SYMBOL, timeframe=TIMEFRAME, limit=MA_LONG)
        df = pd.DataFrame(candles, columns=["timestamp", "open", "high", "low", "close", "volume"])
        df["ma_short"] = df["close"].rolling(MA_SHORT).mean()
        df["ma_long"] = df["close"].rolling(MA_LONG).mean()

        if df["ma_short"].iloc[-2] < df["ma_long"].iloc[-2] and df["ma_short"].iloc[-1] > df["ma_long"].iloc[-1]:
            await bot.send_message(CHAT_ID, f"📈 **BUY SIGNAL**: {SYMBOL} 🚀\nЦена: {df['close'].iloc[-1]} USDT")
        elif df["ma_short"].iloc[-2] > df["ma_long"].iloc[-2] and df["ma_short"].iloc[-1] < df["ma_long"].iloc[-1]:
            await bot.send_message(CHAT_ID, f"📉 **SELL SIGNAL**: {SYMBOL} ⚠️\nЦена: {df['close'].iloc[-1]} USDT")

    except Exception as e:
        print(f"Ошибка: {e}")

async def start_signal_check():
    """Проверяет рынок каждую минуту"""
    while True:
        await get_signal()
        await asyncio.sleep(60)  # Проверяем раз в минуту

async def main():
    """Основная функция запуска бота"""
    asyncio.create_task(start_signal_check())  # Запускаем мониторинг сигналов
    await dp.start_polling(bot)  # Запускаем Telegram-бота

if __name__ == "__main__":
    asyncio.run(main())  # Запуск бота и мониторинга
