import aiohttp
import aiosmtplib

NOTIFICATIONS_FILE = "configs/notifications.conf"
BASE_URL = "https://api.telegram.org/bot"

FULL_URL = None
API_TOKEN = None
MAIL_SERVER = None
PORT_NUMBER = None
SENDER_MAIL = None
SENDER_PASSWORD = None
TRACKERS = {}


class NotificationFuncs:
    def __init__(self, config=None):
        """
        takes attributes from NotificationsConfigurator's object and set them as global variables then deletes the
        object

        :param config: NotificationsConfigurator's object comes from NotificationsConfigurator's constructor
        """

        global API_TOKEN
        global FULL_URL
        global MAIL_SERVER
        global PORT_NUMBER
        global SENDER_MAIL
        global SENDER_PASSWORD
        global TRACKERS

        print("all of the trackers will be passed to global variables from object")

        FULL_URL = config.FULL_URL
        API_TOKEN = config.API_TOKEN
        MAIL_SERVER = config.MAIL_SERVER
        PORT_NUMBER = config.PORT_NUMBER
        SENDER_MAIL = config.SENDER_MAIL
        SENDER_PASSWORD = config.SENDER_PASSWORD
        TRACKERS = config.TRACKERS

        print("all of the trackers were passed to global variables from object")

        del config

    @staticmethod
    async def send_notification(notifications_queue, *messages, msg=None):
        """
        sends messages and email when an asyncio.Queue element is available for get operation; if the element is not
        available method waits an element to be available

        :param notifications_queue: asyncio.Queue of trackers
        :param messages: messages for send to telegram
        :param msg: "email.mime.multipart.MIMEMultipart" objects for send as email
        :return: None
        """

        tracker = await notifications_queue.get()

        aiosmtp_object = aiosmtplib.SMTP(hostname=MAIL_SERVER, port=PORT_NUMBER)
        await aiosmtp_object.connect()
        await aiosmtp_object.starttls()
        await aiosmtp_object.login(SENDER_MAIL, SENDER_PASSWORD)
        msg["From"] = SENDER_MAIL

        try:
            receivers_email_address = TRACKERS['userList'][tracker]['mailAddress']
        except KeyError:
            print("user could not found")
            notifications_queue.task_done()
            return False

        for message in messages:
            requests_string = f"{FULL_URL}sendMessage?chat_id=" \
                              f"{TRACKERS['userList'][tracker]['telegramChatID']}&text={message}"
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(requests_string) as response:
                        if response.status == 200:
                            pass
                        else:
                            print("telegram message could not be sent, status code of response is", response.status)
            except Exception as e:
                print("telegram message could not be sent:", e)

        msg["To"] = receivers_email_address

        try:
            await aiosmtp_object.send_message(msg)
        except aiosmtplib.errors.SMTPServerDisconnected as e:
            print(
                "if you are sending notification mails with gmail services, google may wants to make you wait for a "
                "while")
            print("details:", e)
        except Exception as e:
            print("email could not be sent:", e)
        finally:
            await aiosmtp_object.quit()
            notifications_queue.task_done()
