import json
import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

TOKEN = "7910998632:AAGNBq5PF4a1VTp_tFmoHsUOoqFtYpWmxuA"
ADMIN_ID = 7910998632
DATA_FILE = "pet_data.json"

if os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'r') as f:
        pet_data = json.load(f)
else:
    pet_data = {
        'users': {},
        'banned': [],
        'admins': [ADMIN_ID],
        'moders': [],
        'shop': {
            'cars': {'Лада': 5000, 'BMW': 15000, 'Ferrari': 50000},
            'houses': {'Квартира': 20000, 'Коттедж': 50000, 'Вилла': 100000},
            'items': {'Еда': 100, 'Игрушка': 200, 'Ошейник': 500}
        }
    }

def save_data():
    with open(DATA_FILE, 'w') as f:
        json.dump(pet_data, f, indent=4)

def calculate_level(xp):
    return xp // 1000 + 1

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in pet_data['banned']:
        await update.message.reply_text("🚫 Вы забанены!")
        return
    
    if user_id not in pet_data['users']:
        pet_data['users'][user_id] = {
            'pet': {'name': 'Forchik', 'xp': 0, 'level': 1, 'hunger': 50, 'happiness': 50},
            'money': 1000,
            'inventory': {'cars': [], 'houses': [], 'items': []}
        }
        save_data()
    
    await update.message.reply_text(
        f"🐾 Привет! Я Forchik - твой виртуальный питомец!\n"
        f"🔹 Уровень: {pet_data['users'][user_id]['pet']['level']}\n"
        f"💰 Деньги: {pet_data['users'][user_id]['money']}\n"
        f"🍗 Сытость: {pet_data['users'][user_id]['pet']['hunger']}/100\n"
        f"😊 Настроение: {pet_data['users'][user_id]['pet']['happiness']}/100\n\n"
        "Используй /help для списка команд"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
📜 Доступные команды:
/start - Начать игру
/status - Статус питомца
/feed - Покормить (+10 опыта)
/play - Поиграть (+10 опыта)
/work - Работать (заработать деньги)
/shop - Магазин
/inventory - Инвентарь
/transfer [сумма] [id] - Передать деньги
/game - Мини-игры для опыта

🔐 Админ-команды:
Напишите "админ" для доступа к панели управления
"""
    await update.message.reply_text(help_text)

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in pet_data['users']:
        await update.message.reply_text("Сначала зарегистрируйтесь с помощью /start")
        return
    
    pet = pet_data['users'][user_id]['pet']
    await update.message.reply_text(
        f"🐶 Имя: {pet['name']}\n"
        f"📊 Уровень: {pet['level']}\n"
        f"⭐ Опыт: {pet['xp']}/{pet['level']*1000}\n"
        f"🍗 Сытость: {pet['hunger']}/100\n"
        f"😊 Настроение: {pet['happiness']}/100\n"
        f"💰 Деньги: {pet_data['users'][user_id]['money']}"
    )

def add_xp(user_id, amount):
    pet_data['users'][user_id]['pet']['xp'] += amount
    new_level = calculate_level(pet_data['users'][user_id]['pet']['xp'])
    if new_level > pet_data['users'][user_id]['pet']['level']:
        pet_data['users'][user_id]['pet']['level'] = new_level
        return True
    return False

async def feed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in pet_data['users']:
        await update.message.reply_text("Сначала зарегистрируйтесь с помощью /start")
        return
    
    pet = pet_data['users'][user_id]['pet']
    pet['hunger'] = min(100, pet['hunger'] + 20)
    level_up = add_xp(user_id, 10)
    
    msg = "🍗 Forchik поел! +20 к сытости, +10 опыта"
    if level_up:
        msg += f"\n🎉 Поздравляем! Forchik достиг уровня {pet['level']}!"
    
    await update.message.reply_text(msg)
    save_data()

async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in pet_data['users']:
        await update.message.reply_text("Сначала зарегистрируйтесь с помощью /start")
        return
    
    pet = pet_data['users'][user_id]['pet']
    pet['happiness'] = min(100, pet['happiness'] + 20)
    level_up = add_xp(user_id, 10)
    
    msg = "🎾 Forchik поиграл! +20 к настроению, +10 опыта"
    if level_up:
        msg += f"\n🎉 Поздравляем! Forchik достиг уровня {pet['level']}!"
    
    await update.message.reply_text(msg)
    save_data()

async def work(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in pet_data['users']:
        await update.message.reply_text("Сначала зарегистрируйтесь с помощью /start")
        return
    
    earnings = random.randint(50, 200)
    pet_data['users'][user_id]['money'] += earnings
    await update.message.reply_text(f"💼 Forchik поработал и заработал {earnings} монет!")
    save_data()

async def shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🚗 Машины", callback_data='shop_cars')],
        [InlineKeyboardButton("🏠 Дома", callback_data='shop_houses')],
        [InlineKeyboardButton("🛒 Предметы", callback_data='shop_items')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('🛍️ Что вы хотите купить?', reply_markup=reply_markup)

async def shop_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    category = query.data.split('_')[1]
    
    items = pet_data['shop'][category]
    buttons = []
    for item, price in items.items():
        buttons.append([InlineKeyboardButton(f"{item} - {price} монет", callback_data=f"buy_{category}_{item}")])
    
    buttons.append([InlineKeyboardButton("🔙 Назад", callback_data='shop_back')])
    reply_markup = InlineKeyboardMarkup(buttons)
    await query.edit_message_text(text=f"🛒 Выберите {category}:", reply_markup=reply_markup)

async def buy_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    _, category, item = query.data.split('_')
    price = pet_data['shop'][category][item]
    
    if pet_data['users'][user_id]['money'] >= price:
        pet_data['users'][user_id]['money'] -= price
        pet_data['users'][user_id]['inventory'][category].append(item)
        await query.edit_message_text(f"✅ Вы купили {item} за {price} монет!")
        save_data()
    else:
        await query.edit_message_text("❌ Недостаточно денег!")

async def inventory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in pet_data['users']:
        await update.message.reply_text("Сначала зарегистрируйтесь с помощью /start")
        return
    
    inv = pet_data['users'][user_id]['inventory']
    text = "🎒 Ваш инвентарь:\n"
    text += f"🚗 Машины: {', '.join(inv['cars']) if inv['cars'] else 'Нет'}\n"
    text += f"🏠 Дома: {', '.join(inv['houses']) if inv['houses'] else 'Нет'}\n"
    text += f"🛒 Предметы: {', '.join(inv['items']) if inv['items'] else 'Нет'}"
    await update.message.reply_text(text)

async def transfer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in pet_data['users']:
        await update.message.reply_text("Сначала зарегистрируйтесь с помощью /start")
        return
    
    try:
        amount = int(context.args[0])
        recipient_id = int(context.args[1])
        
        if amount <= 0:
            await update.message.reply_text("❌ Сумма должна быть положительной!")
            return
            
        if user_id == recipient_id:
            await update.message.reply_text("❌ Нельзя перевести себе!")
            return
            
        if pet_data['users'][user_id]['money'] < amount:
            await update.message.reply_text("❌ Недостаточно денег!")
            return
            
        if recipient_id not in pet_data['users']:
            await update.message.reply_text("❌ Получатель не найден!")
            return
            
        pet_data['users'][user_id]['money'] -= amount
        pet_data['users'][recipient_id]['money'] += amount
        await update.message.reply_text(f"✅ Вы перевели {amount} монет пользователю {recipient_id}")
        save_data()
    except:
        await update.message.reply_text("❌ Используйте: /transfer [сумма] [id пользователя]")

async def game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎲 Угадай число", callback_data='game_guess')],
        [InlineKeyboardButton("✂️ Камень-ножницы-бумага", callback_data='game_rps')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('🎮 Выберите игру:', reply_markup=reply_markup)

async def game_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    game_type = query.data.split('_')[1]
    
    if game_type == 'guess':
        context.user_data['game'] = {'type': 'guess', 'number': random.randint(1, 10)}
        await query.edit_message_text("🎲 Я загадал число от 1 до 10. Угадай!")
    elif game_type == 'rps':
        buttons = [
            [InlineKeyboardButton("🪨 Камень", callback_data='rps_rock')],
            [InlineKeyboardButton("✂️ Ножницы", callback_data='rps_scissors')],
            [InlineKeyboardButton("📄 Бумага", callback_data='rps_paper')],
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.edit_message_text("✂️ Выберите:", reply_markup=reply_markup)

async def rps_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_choice = query.data.split('_')[1]
    choices = {'rock': '🪨 Камень', 'scissors': '✂️ Ножницы', 'paper': '📄 Бумага'}
    bot_choice = random.choice(list(choices.keys()))
    
    result = ""
    if user_choice == bot_choice:
        result = "🤝 Ничья!"
        xp = 5
    elif (user_choice == 'rock' and bot_choice == 'scissors') or \
         (user_choice == 'scissors' and bot_choice == 'paper') or \
         (user_choice == 'paper' and bot_choice == 'rock'):
        result = "🎉 Вы победили!"
        xp = 20
    else:
        result = "😢 Вы проиграли!"
        xp = 0
    
    user_id = query.from_user.id
    if xp > 0:
        level_up = add_xp(user_id, xp)
        if level_up:
            result += f"\n🎉 Forchik достиг уровня {pet_data['users'][user_id]['pet']['level']}!"
    
    await query.edit_message_text(
        f"Вы: {choices[user_choice]}\n"
        f"Бот: {choices[bot_choice]}\n"
        f"{result}\n"
        f"+{xp} опыта"
    )
    save_data()

async def guess_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    try:
        guess = int(update.message.text)
        game_data = context.user_data.get('game', {})
        
        if game_data.get('type') != 'guess':
            return
            
        if guess == game_data['number']:
            xp = 30
            level_up = add_xp(user_id, xp)
            msg = f"🎉 Правильно! +{xp} опыта"
            if level_up:
                msg += f"\n🎉 Forchik достиг уровня {pet_data['users'][user_id]['pet']['level']}!"
            await update.message.reply_text(msg)
            context.user_data.pop('game', None)
        elif guess < game_data['number']:
            await update.message.reply_text("⬆️ Больше")
        else:
            await update.message.reply_text("⬇️ Меньше")
    except ValueError:
        pass

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.lower()
    
    if text == "админ" and user_id in pet_data['admins']:
        keyboard = [
            [InlineKeyboardButton("💰 Выдать валюту", callback_data='admin_give_money')],
            [InlineKeyboardButton("❌ Забрать валюту", callback_data='admin_take_money')],
            [InlineKeyboardButton("👑 Выдать админку", callback_data='admin_give_admin')],
            [InlineKeyboardButton("🛡️ Выдать модерку", callback_data='admin_give_moder')],
            [InlineKeyboardButton("🚫 Забрать права", callback_data='admin_remove_rights')],
            [InlineKeyboardButton("📢 Анонс всем", callback_data='admin_announce')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text('🔐 Админ-панель:', reply_markup=reply_markup)
    elif text == "админ":
        await update.message.reply_text("❌ У вас нет прав доступа!")
    else:
        await guess_handler(update, context)

async def admin_panel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    action = query.data.split('_')[1]
    
    if action == 'give_money':
        await query.edit_message_text("Введите ID пользователя и сумму через пробел:\nПример: 123456789 1000")
        context.user_data['admin_action'] = 'give_money'
    elif action == 'take_money':
        await query.edit_message_text("Введите ID пользователя и сумму для изъятия:\nПример: 123456789 500")
        context.user_data['admin_action'] = 'take_money'
    elif action == 'give_admin':
        await query.edit_message_text("Введите ID пользователя для выдачи админки:\nПример: 123456789")
        context.user_data['admin_action'] = 'give_admin'
    elif action == 'give_moder':
        await query.edit_message_text("Введите ID пользователя для выдачи модерки:\nПример: 123456789")
        context.user_data['admin_action'] = 'give_moder'
    elif action == 'remove_rights':
        await query.edit_message_text("Введите ID пользователя для снятия прав:\nПример: 123456789")
        context.user_data['admin_action'] = 'remove_rights'
    elif action == 'announce':
        await query.edit_message_text("Введите сообщение для анонса всем пользователям:")
        context.user_data['admin_action'] = 'announce'

async def admin_action_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in pet_data['admins']:
        await update.message.reply_text("❌ У вас нет прав!")
        return
    
    action = context.user_data.get('admin_action')
    if not action:
        return
    
    try:
        if action == 'announce':
            message = update.message.text
            for user in pet_data['users']:
                try:
                    await context.bot.send_message(
                        chat_id=user,
                        text=f"📢 Важное объявление от администрации:\n\n{message}"
                    )
                except:
                    continue
            await update.message.reply_text("✅ Сообщение отправлено всем пользователям")
        else:
            args = update.message.text.split()
            target_id = int(args[0])
            
            if target_id not in pet_data['users']:
                await update.message.reply_text("❌ Пользователь не найден!")
                return
                
            if action == 'give_money':
                amount = int(args[1])
                pet_data['users'][target_id]['money'] += amount
                await update.message.reply_text(f"✅ Выдано {amount} монет пользователю {target_id}")
                
            elif action == 'take_money':
                amount = int(args[1])
                pet_data['users'][target_id]['money'] = max(0, pet_data['users'][target_id]['money'] - amount)
                await update.message.reply_text(f"✅ Изъято {amount} монет у пользователя {target_id}")
                
            elif action == 'give_admin':
                if target_id not in pet_data['admins']:
                    pet_data['admins'].append(target_id)
                await update.message.reply_text(f"✅ Пользователь {target_id} теперь админ")
                
            elif action == 'give_moder':
                if target_id not in pet_data.get('moders', []):
                    if 'moders' not in pet_data:
                        pet_data['moders'] = []
                    pet_data['moders'].append(target_id)
                await update.message.reply_text(f"✅ Пользователь {target_id} теперь модератор")
                
            elif action == 'remove_rights':
                if target_id in pet_data['admins']:
                    pet_data['admins'].remove(target_id)
                if target_id in pet_data.get('moders', []):
                    pet_data['moders'].remove(target_id)
                await update.message.reply_text(f"✅ Права пользователя {target_id} сброшены")
                
        save_data()
        
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {str(e)}\nПроверьте правильность ввода данных")
    
    context.user_data.pop('admin_action', None)

def run_bot():
    application = Application.builder().token(TOKEN).build()

    # Основные команды
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("feed", feed))
    application.add_handler(CommandHandler("play", play))
    application.add_handler(CommandHandler("work", work))
    application.add_handler(CommandHandler("shop", shop))
    application.add_handler(CommandHandler("inventory", inventory))
    application.add_handler(CommandHandler("transfer", transfer))
    application.add_handler(CommandHandler("game", game))
    
    # Обработчики магазина
    application.add_handler(CallbackQueryHandler(shop_handler, pattern='^shop_'))
    application.add_handler(CallbackQueryHandler(buy_handler, pattern='^buy_'))
    application.add_handler(CallbackQueryHandler(lambda u,c: u.edit_message_text("🔙"), pattern='^shop_back$'))
    
    # Обработчики игр
    application.add_handler(CallbackQueryHandler(game_handler, pattern='^game_'))
    application.add_handler(CallbackQueryHandler(rps_handler, pattern='^rps_'))
    
    # Админ-система
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    application.add_handler(CallbackQueryHandler(admin_panel_handler, pattern='^admin_'))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, admin_action_handler))
    
    # Запуск бота
    application.run_polling()

if __name__ == '__main__':
    run_bot()