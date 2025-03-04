import os
import ccxt.async_support as ccxt
import asyncio
import numpy as np
import pandas as pd
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode

# 🔹 Настройки
API_TOKEN = os.getenv("8153754798:AAGY5YkGcq9iNc_bhF62Q73wSJgv8aO7ZRk")
CHAT_ID = os.getenv("178010516")
SYMBOL = "BTC/USDT"
EXCHANGE_NAME = "binance"
MA_SHORT = 7
MA_LONG = 25
TIMEFRAME = "1h"

# 🔹 Подключаем Telegram-бота
bot = Bot(token=API_TOKEN, parse_mode=ParseMode.MARKDOWN)
dp = Dispatcher()

# 🔹 Подключаемся к бирже
exchange = getattr(ccxt, EXCHANGE_NAME)({'rateLimit': 1200})

async def get_signal():
    """Проверка пересечения скользящих средних и отправка сигналов"""
    try:
        candles = await exchange.fetch_ohlcv(SYMBOL, timeframe=TIMEFRAME, limit=MA_LONG)
        df = pd.DataFrame(candles, columns=["timestamp", "open", "high", "low", "close", "volume"])
        df["ma_short"] = df["close"].rolling(MA_SHORT).mean()
        df["ma_long"] = df["close"].rolling(MA_LONG).mean()

        if df["ma_short"].iloc[-2] < df["ma_long"].iloc[-2] and df["ma_short"].iloc[-1] > df["ma_long"].iloc[-1]:
            await bot.send_message(CHAT_ID, f"📈 **BUY SIGNAL**: {SYMBOL} 🚀\nЦена: {df['close'].iloc[-1]} USDT")
        elif df["ma_short"].iloc[-2] > df["ma_long"].iloc[-2] and df["ma_short"].iloc[-1] < df["ma_long"].iloc[-1]:
            await bot.send_message(CHAT_ID, f"📉 **SELL SIGNAL**: {SYMBOL} ⚠️\nЦена: {df['close'].iloc[-1]} USDT")

    except Exception as e:
        print(f"Ошибка: {e}")

async def start_bot():
    """Запускаем бота и проверяем рынок каждую минуту"""
    while True:
        await get_signal()
        await asyncio.sleep(60)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
