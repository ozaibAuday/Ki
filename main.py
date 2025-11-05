import requests
import base64
from telebot import TeleBot, types

API_TOKEN = "5086918397:AAEYjm4Vucfa-g3aLZ23HndyZbunj1FEVoA"
CHANNEL_USERNAME = "@Toiii" 
bot = TeleBot(API_TOKEN)
 
class ImageConverter:
    def convert_image_to_base64(self, file_data):
        return base64.b64encode(file_data).decode('utf-8')

    def call_google_vision_api(self, encoded_image):
        headers = {
            'User-Agent': 'Google-API-Java-Client Google-HTTP-Java-Client/1.43.3 (gzip)',
            'x-android-package': 'image.to.text.ocr',
            'x-android-cert': 'ad32d34755bb3b369a2ea8dfe9e0c385d73f80f0',
            'Content-Type': 'application/json; charset=UTF-8',
            'Host': 'vision.googleapis.com',
            'Connection': 'Keep-Alive'
        }
        params = {'key': 'AIzaSyA5MInkpSbdSbmozCQSuBY3pylSTgmLlaM'}
        json_data = {
            'requests': [
                {
                    'features': [
                        {
                            'maxResults': 10,
                            'type': 'TEXT_DETECTION'
                        }
                    ],
                    'image': {
                        'content': encoded_image
                    }
                }
            ]
        }
        response = requests.post('https://vision.googleapis.com/v1/images:annotate', params=params, headers=headers, json=json_data)
        return response.json() if response.status_code == 200 else "Error: " + response.text

def is_subscribed(user_id):
    """
    تم تطوير الملف بواسطة المطور منتظر .
    """
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if not is_subscribed(message.from_user.id):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("رابط الأشتراك .", url=f"https://t.me/{CHANNEL_USERNAME.strip('@')}"))
        bot.send_message(
            message.chat.id,
            "عليك الاشتراك في القناة لاستخدام البوت .",
            reply_markup=markup
        )
    else:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("• Dev", url="https://t.me/rr8r9"))
        bot.send_message(
            message.chat.id, 
            "أهلاً عزيزي، وضيفتي قرأءة نصوص الصور بدقة كبيرة، تم تطويري عبر واجهة برمجة تطبيقات جوجل .",
            reply_markup=markup
        )

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    if not is_subscribed(message.from_user.id):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("- رابط الأشتراك .", url=f"https://t.me/{CHANNEL_USERNAME.strip('@')}"))
        bot.send_message(
            message.chat.id,
            "يجب عليك الاشتراك في القناة لاستخدام البوت.",
            reply_markup=markup
        )
        return

    waiting_message = bot.send_message(message.chat.id, "- انتضر قليلاً ...")
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        converter = ImageConverter()
        
        encoded_image = converter.convert_image_to_base64(downloaded_file)
        vision_response = converter.call_google_vision_api(encoded_image)
        bot.delete_message(message.chat.id, waiting_message.id)
        if 'responses' in vision_response and vision_response['responses']:
            texts = [text['description'] for text in vision_response['responses'][0].get('textAnnotations', [])]
            if texts:
                extracted_text = texts[0]
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton("نسخ النص", callback_data="copy_text"))
                bot.send_message(message.chat.id, f"النص المستخرج :\n```{extracted_text}```", parse_mode="Markdown", reply_markup=markup)
            else:
                bot.send_message(message.chat.id, "لم يتم العثور على نص في الصورة.")
        else:
            bot.send_message(message.chat.id, f"خطأ من API: {vision_response}")
    except Exception as e:
        bot.delete_message(message.chat.id, waiting_message.id)
        bot.send_message(message.chat.id, f"حدث خطأ أثناء معالجة الصورة: {e}")

@bot.callback_query_handler(func=lambda call: call.data == "copy_text")
def handle_copy_text(call):
    bot.answer_callback_query(call.id, "تم نسخ النص بنجاح .")

bot.infinity_polling()
