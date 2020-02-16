from src.Video import Video
from src.CacheServer import CacheServer
from src.Request import Request
from src.Endpoint import Endpoint

from collections import defaultdict

def read_txt(filename):
    f = open(filename, 'r')

    V, E, R, C, X = map(int, f.readline().replace('\n', '').split(' '))

    videos = [Video(int(x)) for x in f.readline().replace('\n', '').split(' ')]

    caches = [CacheServer(X) for _ in range(C)]

    endpoints = []

    for i in range(E):
        L, K = map(int, f.readline().rstrip('\n').split(' '))
        endpoints.append(Endpoint(L))
        for j in range(K):
            cache, latency = map(int, f.readline().rstrip('\n').split(' '))
            endpoints[-1].caches.add(CacheServer.by_id[cache])
            endpoints[-1].cache_latency[CacheServer.by_id[cache]] = latency

    requests = [Request.from_str(f.readline().rstrip('\n'), videos, endpoints) for _ in range(R)]

    f.close()
    return videos, caches, endpoints, requests


def calculate_requests_per_video(requests):
    # Lists requests for a particular video
    video_requests = defaultdict(set)
    for r in requests:
        video_requests[r.video].add(r)
    return video_requests
