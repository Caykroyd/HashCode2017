from src.Video import Video
from src.Endpoint import Endpoint

class Request:
    id = 0
    by_id = {}
    def __init__(self, video, endpoint, count):
        self.video = video
        self.endpoint = endpoint
        self.count = count

        self.id = Request.id
        Request.by_id[self.id] = self
        Request.id += 1

    @staticmethod
    def from_str(txt, videos, endpoints):
        l = txt.split(' ')
        V, E, C = map(int, l)
        return Request(Video.by_id[V], Endpoint.by_id[E], C)

    def current_latency(self):
        '''
        Calculates the latency currently measured to execute this request, i.e.,
        the latency between the request's endpoint and the closest video cache
        (or data center).
        Optimized to run fast if no caches are found.
        '''
        dc_latency = self.endpoint.data_center_latency
        if(len(self.video.caches) == 0):
          return dc_latency
        caches = self.video.caches & self.endpoint.caches
        if(len(caches) == 0):
          return dc_latency
        cache_latency = self.endpoint.cache_latency
        return min(cache_latency[c] for c in caches)

    def __hash__(self):
        return self.id
