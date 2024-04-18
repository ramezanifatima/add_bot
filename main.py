from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, \
    CallbackQueryHandler, CallbackContext
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload
from authlib.integrations.requests_client import OAuth2Session
from google.oauth2.credentials import UserAccessTokenCredentials


# ====================================================================
async def create_access_token(update, contex):
    print('ایجاد توکن ')
    client_id = "CLIENT ID"
    client_secret = "CLIENT SECRET"
    redirect_uri = "REDIRECT URL"
    scope = ['SCOP']

    # Create OAuth2 session
    token_url = 'TOKEN URL'
    auth_url = 'AUTH URL'
    oauth = OAuth2Session(client_id=client_id, redirect_uri=redirect_uri, scope=scope)

    # Get authorization URL
    authorization_url, state = oauth.create_authorization_url(auth_url)
    await contex.bot.send_message(chat_id=update.effective_chat.id, text=authorization_url)


def check_token(token):
    print('چک کردن  توکن ')
    client_id = "CLIENT ID"
    client_secret = "CLIENT SECRET"
    redirect_uri = "REDIRECT URL"
    scope = ['SCOP']

    # Create OAuth2 session
    token_url = 'TOKEN URL'
    auth_url = 'AUTH URL'
    authorization_response = token
    # Fetch access token
    oauth = OAuth2Session(client_id=client_id, redirect_uri=redirect_uri, scope=scope)
    token = oauth.fetch_token(token_url, authorization_response=authorization_response,
                              client_secret=client_secret, include_client_id=False
                              )
    access_token = token['access_token']
    return access_token


async def upload_file_to_google_drive(access_token, file_path, folder_id=None):
    # توکن دسترسی
    # ایجاد یک اتصال به API Google Drive
    print('اپلود فایل')
    creds = Credentials(token=access_token)
    service = build('drive', 'v3', credentials=creds)

    file_metadata = {'name': file_path.split('/')[-1]}
    if folder_id:
        file_metadata['parents'] = [folder_id]

    # آپلود فایل
    media = MediaFileUpload(file_path)
    file = await service.files().create(body=file_metadata, media_body=media, fields='id').execute()


    print(f"File '{file_path.split('/')[-1]}' uploaded successfully to Google Drive with ID: {file.get('id')}")

    print(f"File uploaded successfully!")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await create_access_token(update, context)
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text='بر روی لینکی که برای شما ارسال شده است بروید و توکن دسترسی که برای شما در صفحه اخر در نوار ادرس مرورگر خود ارسال میشود را کپی کنید و به ربات بفرستید ')


async def ch_t(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text:
        print("توکن دریافت شد")
        await context.bot.send_message(chat_id=update.effective_chat.id,text='فایل حود را بفرستید')

        token = update.message.text
        acc_token = check_token(token)

        return acc_token


async def upload_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print('start')
    if update.message.document:

        acc_token = await ch_t(update, context)
        print('accses token is load')
        print(acc_token)

        print('upload fil start')
        file_name = 'file'
        new_file = await update.message.effective_attachment.get_file()
        await new_file.download_to_drive(file_name)
        await create_access_token(update, context)
        await upload_file_to_google_drive(access_token=acc_token, file_path=file_name)

    else:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text='لطفاً یک فایل ارسال کنید.')


if __name__ == '__main__':
    application = ApplicationBuilder().token('TOKEN').build()
    start_handler = CommandHandler('start', start)
    upload_handler = MessageHandler(callback=upload_file, filters=filters.ALL)
    application.add_handler(start_handler)
    application.add_handler(upload_handler)
    application.run_polling()
