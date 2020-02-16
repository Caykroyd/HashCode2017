class Video:
    id = 0
    by_id = {}
    def __init__ (self, size):
        self.size = size
        self.caches = set() # Caches which contain these videos

        self.id = Video.id
        Video.by_id[self.id] = self
        Video.id += 1

    def __hash__(self):
        return self.id
