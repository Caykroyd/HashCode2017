from src.Video import Video
from src.CacheServer import CacheServer
from src.Request import Request
from src.Endpoint import Endpoint

from src.Processing import read_txt, calculate_requests_per_video

from collections import defaultdict
import os.path as osp

def heuristic(v : Video, c : CacheServer, r : Request, l : int, W : float = 0):
    '''
    The heuristic for score gain. Given a request, what would be the gain if we
    added video v to cache server c?
        - W is a penalization for large video sizes
    Complexity: C(r)
    '''
    return (r.current_latency() - l) * r.count * (1 - W * v.size)

def construct_score_graph(videos, val_func = heuristic):
    '''
    For each (Video, CacheServer) pair calculates the respective score gain by
    adding the video to server. For score calculation we use the output of:
        -   val_func(Video, CacheServer, Request, int : latency)
    Additionally we save all the pairs (int : latency, Request) associated to
    each (Video, CacheServer) pair.
    Complexity: Sum_{r in R}{ C(r) * val_func } < R * C * val_func
    '''
    scores = defaultdict(float)
    latencies = defaultdict(list)
    steps = 0
    for v in videos:
        #print('Video',v.id)
        # find requests that are about video
        reqs = video_requests[v]
        for r in reqs:
            for c in r.endpoint.caches:
                l = r.endpoint.cache_latency[c]
                score = val_func(v, c, r, l)
                if(score > 0):
                    scores[(v.id, c.id)] += score
                latencies[(v.id, c.id)].append((l, r)) # save the latency that associates a video, cache server and request
                steps += 1
                if(steps % 1e5 == 0):
                  print('Step %d.' % steps)
    print('Matrix Constructed in %d steps.' % steps)

    return scores, latencies

import heapq
def add_videos_to_caches(scores : dict, latencies, val_func = heuristic):
    '''
    Sequentially adds videos to cache-servers by, at each step, taking the
    (Video, CacheServer) pair which maximizes gain. Gain is given by parameter:
        -   val_func(Video, CacheServer, Request, int : latency)
    This is done by taking a pre-calculated dictionary of below format, and
    transforming it into a priority queue, updating the values as necessary.
        -   (Video.id, CacheServer.id) -> int : precomputed_scores
    '''
    # Sort video/cache pairs by score. Since we use a minheap (priority queue),
    # scores must be negative when we heapify (we want to take scores with greatest
    # absolute value, in order).
    print('L =',len(scores))
    keys = sorted(((-scores[k], k) for k in scores.keys()))
    print('Sorted.')
    heapq.heapify(keys)
    print('Heapified.')

    added_videos = set()
    executed_steps, wasted_steps = 0, 0
    while(len(keys) > 0):
        if((executed_steps + wasted_steps) % 1e5 == 0):
            print('Dynamic Step [Executed Steps: %d, Wasted Steps %d].' % (executed_steps, wasted_steps))
        s, (v, c) = heapq.heappop(keys);
        s = -s # score is negative since it's a minheap (we want to maximize score)
        video, cache = Video.by_id[v], CacheServer.by_id[c]

        if(v in added_videos):
          # If the score has changed from previous iterations, that means the new
          # score is lower than the previous score. So we can just put it back in
          # the heap and pick next (highest-score) value
          score = sum(val_func(video, cache, req, lat) for (lat, req) in latencies[(v,c)])
          if(score < s):
              heapq.heappush(keys, (-score, (v, c)))
              wasted_steps += 1
              continue

        # if the video fits into the cache, great - add it in. If it doesn't,
        # too bad - we'll never see this video/cache pair again.
        if cache.remaining_size > video.size:
            cache.add_video(video)
            added_videos.add(v)

        executed_steps += 1
    print('Done [Executed Steps: %d, Wasted Steps %d].' % (executed_steps, wasted_steps))

files = ['me_at_the_zoo.in', 'videos_worth_spreading.in', 'trending_today.in', 'kittens.in.txt']

f = files[1]
filename = osp.join('in', f)

W = {'me_at_the_zoo.in': 1.5e-2, 'videos_worth_spreading.in' : 1.42e-3, 'trending_today.in' : 1e-4, 'kittens.in.txt' : 6.5e-4}
W = W[f]

val_func = lambda v, c, r, l : heuristic(v, c, r, l, W)

videos, caches, endpoints, requests = read_txt(filename)
print('Inputs Parsed.')

video_requests = calculate_requests_per_video(requests)
print('Preprocessing done.')

# Main algorithm
score_priority_queue, latencies = construct_score_graph(videos, val_func = val_func)
add_videos_to_caches(score_priority_queue, latencies, val_func = val_func)

def score(requests):
    r_total_count = sum(r.count for r in requests)
    raw_score = sum((r.endpoint.data_center_latency - r.current_latency()) * r.count for r in requests)
    return 1000 * raw_score / r_total_count

print('File:', filename, "\nScore =", score (requests))

print('Packing Factor:', sum(c.remaining_size for c in caches) / sum(c.size for c in caches))
