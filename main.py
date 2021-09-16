import asyncio
from notifications.notification_list import NotificationList
from notifications.notification_configurator import NotificationConfigurator

# usernames, comes from application flow
users = ["user_a", "user_b"]


# sample of how to use
class Test:
    def __init__(self):
        asyncio.get_event_loop().run_until_complete(self.test())

    async def test(self):
        # check "notification_list.py" for different notification methods
        task = asyncio.create_task(NotificationList.notify_users_about_x(users, "argument_a", "argument_b"))
        print("the application flow does not wait for sending notification, it continues...")
        await task
        print("sending messages done!")


# it is better to call this constructor in your applications cli.py file or starting point of the your applications flow
NotificationConfigurator()

Test()

x = input("type anything to exit")







