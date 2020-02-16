class CacheServer:
    id = 0
    by_id = {}
    def __init__(self, size):
        self.size = size
        self.videos = set()
        self.remaining_size = self.size

        self.id = CacheServer.id
        CacheServer.by_id[self.id] = self
        CacheServer.id += 1

    def add_video(self, video):
        assert self.remaining_size >= video.size
        self.videos.add(video)
        self.remaining_size -= video.size
        video.caches.add(self)

    def stored_videos(self):
        '''
        Outputs the list of videos stored in this cache as a string.
        '''
        ids = map(lambda r: str(r.id), self.videos)
        return ' '.join(ids)

    def __hash__(self):
        return self.id
