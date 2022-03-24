import ast

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from services import *
# step = {"state": 0}

forcontact = ReplyKeyboardMarkup([[KeyboardButton("Contactni yuborish", request_contact=True)]], resize_keyboard=True)


def key_btns(type=None, ctg=None):
    btn = []
    if type == 'menu':
        ctgs = get_ctgs()
        for i in range(1, len(ctgs), 2):
            btn.append([
                KeyboardButton(ctgs[i-1][1]),
                KeyboardButton(ctgs[i][1])
            ])

        if len(ctgs) % 2:
            btn.append([KeyboardButton(ctgs[-1][1])])

        btn.append([
            KeyboardButton("📥 Savat"), KeyboardButton("⬅️ Ortga")
        ])


    elif type == 'ctg':
        prod = get_products(ctg=ctg)

        for i in range(1, len(prod), 2):
            btn.append([
                KeyboardButton(prod[i-1][1]),
                KeyboardButton(prod[i][1]),
            ])

        if len(prod) % 2:
            btn.append([KeyboardButton(prod[-1][1])])

        btn.append([
            KeyboardButton("⬅️ Ortga")
        ])


    elif type == "number":
        for i in range(1, 10, 3):
            btn.append([
                InlineKeyboardButton(f'{i}', callback_data=f'{i}'),
                InlineKeyboardButton(f'{i+1}', callback_data=f'{i+1}'),
                InlineKeyboardButton(f'{i+2}', callback_data=f'{i+2}')
            ])

        btn.append([InlineKeyboardButton('⬅️ Ortga', callback_data='back')])


        return InlineKeyboardMarkup(btn)


    else:
        btn = [
            [KeyboardButton("🍴 Меню")],
            [KeyboardButton("🛍 Мои заказы")],
            [KeyboardButton("✍️ Оставить отзыв"), KeyboardButton("⚙️ Настройки")]
        ]

    return ReplyKeyboardMarkup(btn, resize_keyboard=True)


def start(update, context):
    user = update.message.from_user
    step = get_log(user.id)
    if step is None:
        step = create_log(user.id)
    step = ast.literal_eval(step[1])
    step['state'] = 1

    tg_user = get_user(user.id)
    if tg_user is not None:
        step['state'] = 4
        clear_log(user.id, 4)
        update.message.reply_text("Menyulardan birini tanlang👇", reply_markup=key_btns())
        return 0

    update.message.reply_text("Assolom alykum\nIsmingizni kiriting")

    change_log(user.id, step)


def recieved_msg(update, context):
    user = update.message.from_user
    step = get_log(user.id)
    step = ast.literal_eval(step[1])

    msg = update.message.text
    state = step.get('state', 0)

    if msg == "🍴 Меню":
        update.message.reply_text("Bolimni tanlang", reply_markup=key_btns('menu'))
        step['state'] = 5

    if state == 1:
        step['ism'] = msg
        step['state'] = 2
        update.message.reply_text("Familiyangizni kiriting")
    elif state == 2:
        step['familiya'] = msg
        step['state'] = 3
        update.message.reply_text("Contactizni yuboring", reply_markup=forcontact)

    elif state == 5:
        if msg == "⬅️ Ortga":
            step['state'] = 4
            clear_log(user.id, 4)
            update.message.reply_text("Menyulardan birini tanlang👇", reply_markup=key_btns())
        else:
            step['state'] = 6
            category = get_ctg(ctg=msg)
            step['ctg'] = msg
            update.message.reply_text("Quyidagi mahsulotlardan birini tanlang",
                                      reply_markup=key_btns('ctg',ctg=msg))
            context.bot.send_photo(photo=open(category[3], 'rb'),
                                   caption=f"{category[1]}", chat_id=user.id)
    elif state == 6:
        if msg == "⬅️ Ortga":
            step['state'] = 5
            update.message.reply_text("Menyulardan birini   tanlang👇", reply_markup=key_btns('menu'))
        else:
            step['state'] = 7
            product = get_products(name=msg)
            step['price'] = product[3]
            step['prod'] = product[1]
            context.bot.send_photo(photo=open(product[5], 'rb'),
                                   caption=f"{product[1]}, \nNarhi: {product[3]}",
                                   chat_id=user.id,
                                   reply_markup=key_btns(type='number'))
    elif state == 7:
        if msg == "⬅️ Ortga":
            step['state'] = 6
            update.message.reply_text("Quyidagi mahsulotlardan birini tanlang",
                                      reply_markup=key_btns('ctg' ,ctg=step.get('ctg', '')))
            update.message.reply_text("Menyulardan birini   tanlang👇", reply_markup=key_btns('menu'))

    change_log(user.id, step)


def contact_handler(update, context):
    user = update.message.from_user
    step = get_log(user.id)
    step = ast.literal_eval(step[1])
    contact = update.message.contact
    state = step.get('state', 0)
    if state == 3:
        step['state'] = 4
        step['raqam'] = contact.phone_number
        add_user(user.id, step)
        clear_log(user.id, 4)
        update.message.reply_text("Menyulardan birini tanlang👇", reply_markup=key_btns())

    change_log(user.id, step)


def inline_handler(update, context):
    query = update.callback_query
    user = query.from_user
    data = query.data

    step = get_log(user.id)
    step = ast.literal_eval(step[1])
    state = step.get('state', 0)
    if state == 7:
        if data == 'back':
            query.message.delete()
            step['state'] = 6
            query.message.reply_text(text="Quyidagi mahsulotlardan birini tanlang",
                                      reply_markup=key_btns('ctg',ctg=step['ctg']))

        else:
            step['state'] = 6
            query.message.delete()
            query.message.reply_text(text=f"Umumiy narh: {int(data) * step.get ('price', 0)}")

    change_log(user.id, step)


def main():
    updater = Updater("5105408750:AAHos0K_4DOlycJCo8P1WiuZPx4KAmY7YGE")
    updater.dispatcher.add_handler(CommandHandler("start", start))
    updater.dispatcher.add_handler(MessageHandler(Filters.text, recieved_msg))
    updater.dispatcher.add_handler(MessageHandler(Filters.contact, contact_handler))
    updater.dispatcher.add_handler(CallbackQueryHandler(inline_handler))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
