from InstagramAPI import InstagramAPI


class Instagram:
    def __init__(self, username, password):
        self.api = InstagramAPI(username, password)

    def test(self):
        if self.api.login():
            self.api.getSelfUserFeed()  # get self user feed
            print(self.api.LastJson)  # print last response JSON
            print("Login success!")
        else:
            print("Can't login!")

    def get_total_followers(self):
        self.api.login()
        followers = []
        next_max_id = True
        while next_max_id:
            # first iteration hack
            if next_max_id is True:
                next_max_id = ''

            _ = self.api.getUserFollowers(self.api.username_id, maxid=next_max_id)
            followers.extend(self.api.LastJson.get('users', []))
            next_max_id = self.api.LastJson.get('next_max_id', '')
        return followers

    def upload_album(self, photos, videos, caption):
        media = []
        for photo in photos:
            media.append({'type': 'photo', 'file': photo})
        for video in videos:
            media.append({'type': 'video', 'file': video})

        self.api.login()
        self.api.uploadAlbum(media, caption)

    def upload_video(self, video, caption):
        self.api.login()
        self.api.uploadVideo(video, caption)

    def upload_photo(self, photo, caption):
        self.api.login()
        test = self.api.uploadPhoto(photo=photo, caption=caption)
        print(test)
