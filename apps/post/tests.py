from django.test import TestCase
from instabot import Bot


# Create your tests here.
def test_album():
    bot = Bot()
    bot.login()
    media = [  # Albums can contain between 2 and 10 photos/videos.
        {
            'type': 'photo',
            'file': '/home/mehdi/Pictures/nature1.jpeg',  # Path to the photo file.
            # 'usertags': [
            #     {  # Optional, lets you tag one or more users in a PHOTO.
            #         'position': [0.5, 0.5],
            #         # WARNING: THE USER ID MUST BE VALID. INSTAGRAM WILL VERIFY IT
            #         # AND IF IT'S WRONG THEY WILL SAY "media configure error".
            #         'user_id': '123456789',  # Must be a numerical UserPK ID.
            #     },
            # ]
        },
        {
            'type': 'photo',
            'file': '/home/mehdi/Pictures/nature2.jpg',  # Path to the photo file.
        },

        # {
        #     'type': 'photo',
        #     'file': '/home/mehdi/Pictures/nature3.jpeg',  # Path to the photo file.
        # },

    ]
    bot.api.upload_album(media, caption="album test")
