import numpy as np
from os import listdir
from os.path import isfile, join

# 5 2 4 3 100
# 50 50 80 30 110
# 1000 3
# 0 100
# 2 200
# 1 300
# 500 0
# 3 0 1500
# 0 1 1000
# 4 0 500
# 1 0 1000
# 5 videos, 2 endpoints, 4 request descriptions, 3 caches 100MB each.
# Videos 0, 1, 2, 3, 4 have sizes 50MB, 50MB, 80MB, 30MB, 110MB.
# Endpoint 0 has 1000ms datacenter latency and is connected to 3 caches:
# The latency (of endpoint 0) to cache 0 is 100ms.
# The latency (of endpoint 0) to cache 2 is 200ms.
# The latency (of endpoint 0) to cache 1 is 300ms.
# Endpoint 1 has 500ms datacenter latency and is not connected to a cache.
# 1500 requests for video 3 coming from endpoint 0.
# 1000 requests for video 0 coming from endpoint 1.
# 500 requests for video 4 coming from endpoint 0.
# 1000 requests for video 1 coming from endpoint 0.

class Cache:
    def __init__(self, idx, size):
        self.idx = idx
        self.size = size
        self.cached_video = set()
    def add_video(self, video_idx, video_size):
        if self.size < video_size:
            print("[Error] Cache is already FULL!!!")
            return
        self.cached_video.add(video_idx)
        self.size -= video_size
    def get_capacity(self):
        return self.size
    def is_video_exist(self, video_idx):
        return video_idx in self.cached_video

class Endpoint:
    def __init__(self, idx, latency, n_cache_endpoint, cache_latency_map):
        self.idx = idx
        self.latency = latency
        self.n_cache_endpoint = n_cache_endpoint
        self.cache_latency_map = cache_latency_map
    def get_cache_latency(self, cache_idx):
        if cache_idx in self.cache_latency_map:
            return self.cache_latency_map[cache_idx]
        return -1
    def get_cache_number(self):
        return self.cache_latency_map.size()
    def get_connected_cache(self):
        return self.cache_latency_map.key()

class Request:
    def __init__(self, idx, video_idx, endpoint_idx, n_user_request):
        self.idx = idx
        self.video_idx = video_idx
        self.endpoint_idx = endpoint_idx
        self.n_user_request = n_user_request


def get_input_data(path_to_file):
    with open(path_to_file) as f:
        n_video, n_endpoint, n_request, n_cache, cache_size = [int(i) for i in f.readline().strip().split()]
        video_size_array = [int(i) for i in f.readline().strip().split()]

        caches = [Cache(i, cache_size) for i in range(n_cache)]

        endpoints = []
        requests = []

        for endpoint_idx in range(n_endpoint):
            latency, n_cache_endpoint = [int(i) for i in f.readline().strip().split()]

            endpoint_cache_latency_map = {}
            for i in range(n_cache_endpoint):
                cache_idx, endpoint_cache_latency = [int(i) for i in f.readline().strip().split()]
                endpoint_cache_latency_map[cache_idx] = endpoint_cache_latency

            endpoints.append(Endpoint(endpoint_idx, latency, n_cache_endpoint, endpoint_cache_latency_map))

        for request_idx in range(n_request):
            video_idx, endpoint_idx, n_user_request = [int(i) for i in f.readline().strip().split()]
            requests.append(Request(request_idx, video_idx, endpoint_idx, n_user_request))

        return endpoints, requests, caches, video_size_array, n_video, n_endpoint, n_request

def write_result(caches, path_to_output):
    n_cache_used = 0
    result = []
    for cache in caches:
        if len(cache.cached_video) == 0:
            continue
        
        n_cache_used += 1
        result_cache = list(cache.cached_video)
        result_cache.insert(0, cache.idx)
        result.append(" ".join(str(v) for v in result_cache) + "\n")

    result.insert(0, "{}\n".format(str(n_cache_used)))
    with open(path_to_output, 'w') as f:
        f.writelines(result)

def grading(path_to_output, requests, endpoints, silence):
    score = 0
    total_request_from_user = 0
    with open(path_to_output) as f:
        n_cache_used = int(f.readline().strip())
        cache_to_video = {}
        video_to_cache = {}
        for cache_idx in range(n_cache_used):
            cached_info = [int(i) for i in f.readline().strip().split()]

            cache_to_video[cached_info[0]] = cached_info[1:]
            for video_idx in cached_info[1:]:
                if video_idx in video_to_cache.keys():
                    video_to_cache[video_idx].append(cached_info[0])
                else:
                    video_to_cache[video_idx] = [cached_info[0]]

        for req in requests:
            total_request_from_user += req.n_user_request
            video_in_cache_set = None
            if req.video_idx in video_to_cache.keys():
                video_in_cache_set = set(video_to_cache[req.video_idx])

            else:
                if silence:
                    pass
                else:
                    print("[[Request {}]]".format(req.idx))
                    print("video {} required from endpoint {} is not cached, \nscore += 0".format(req.video_idx, req.endpoint_idx))
                continue

            cache_in_x_endpoint = endpoints[req.endpoint_idx].cache_latency_map
            min_endpoint_to_cache_latency = -1
            cache_idx_min_latency = None
            for cache_idx, endpoint_to_cache_latency in cache_in_x_endpoint.items():
                if cache_idx in video_in_cache_set:
                    if min_endpoint_to_cache_latency == -1:
                        min_endpoint_to_cache_latency = endpoint_to_cache_latency
                        cache_idx_min_latency = cache_idx
                    elif endpoint_to_cache_latency < min_endpoint_to_cache_latency:
                        min_endpoint_to_cache_latency = endpoint_to_cache_latency
                        cache_idx_min_latency = cache_idx
                    else:
                        pass
            # not cached in connected cache
            if cache_idx_min_latency is None:
                if silence:
                    pass
                else:
                    print("[[Request {}]]".format(req.idx))
                    print("Endpoint {} has no caches containing required video {}, \nscore += 0".format( req.video_idx, req.endpoint_idx))
            else:
                add_score = req.n_user_request * (endpoints[req.endpoint_idx].latency - min_endpoint_to_cache_latency)
                if silence:
                    pass
                else:
                    print("[[Request {}]]".format(req.idx))
                    print("video {} required from endpoint {} is cached in connected cache {}, \nscore += {}".format(
                        req.video_idx, req.endpoint_idx, cache_idx_min_latency, add_score))
                score += add_score
    if silence:
        pass
    else:
        print("==========================================================")      
        print("TOTAL SCORE for {}: {}".format(path_to_output, round(1000 * score/(total_request_from_user))))
        print("==========================================================")        
    return round(1000 * score/(total_request_from_user))

if "__main__" == __name__:
    TEST_ON_ALL_DATA = True
    
    # for test single data file
    _path_to_file = "/home/open/hashcode/test.in"
    _path_to_output = "/home/open/hashcode/test.out"
    # for test all data
    path_to_out_dir = "/home/open/hashcode/out"
    path_to_in_dir = "/home/open/hashcode/qualification_round_2017.in"
    all_in_data_file_path = [f for f in listdir(path_to_in_dir) if isfile(join(path_to_in_dir, f))]
    
    def get_full_path(dir_path, filename):
            return join(dir_path, filename)

    def test_on_one_file(path_to_file, path_to_output, silence = False):
        endpoints, requests, caches, video_size_array, n_video, n_endpoint, n_request = get_input_data(path_to_file)
        
        get_video_size = lambda video_idx: video_size_array[video_idx]
        
        requests = sorted(requests, key = lambda request : endpoints[request.endpoint_idx].latency * request.n_user_request, reverse = True)
        # requests = sorted(requests, key = lambda request : request.n_user_request, reverse = True) 

        for req in requests:
            # check the fastest cache in the endpoint
            endpoint_idx = req.endpoint_idx
            connected_cache_contain_such_video = False

            for cache_idx, cache_latency_to_endpoint in endpoints[endpoint_idx].cache_latency_map.items():
                if caches[cache_idx].is_video_exist(req.video_idx):
                    connected_cache_contain_such_video = True
                    break

            if connected_cache_contain_such_video == False:
                for cache_idx, cache_latency_to_endpoint in endpoints[endpoint_idx].cache_latency_map.items():
                    cap = caches[cache_idx].get_capacity()
                    video_size = get_video_size(req.video_idx)
                    if cap >= video_size:
                        caches[cache_idx].add_video(req.video_idx, video_size)
                        break
                    else:
                        pass
            
        write_result(caches, path_to_output)
        return grading(path_to_output, requests, endpoints, silence)

    if TEST_ON_ALL_DATA:
        list_scores = []
        total_score = 0
        for filename in all_in_data_file_path:
            path_to_file = get_full_path(path_to_in_dir, filename)
            path_to_output = get_full_path(path_to_out_dir, filename) + ".out"
            
            score = test_on_one_file(path_to_file, path_to_output, True)
            list_scores.append(score)
            total_score += score

        for i in range(len(all_in_data_file_path)):
            print("{0:<30} => {1}".format(all_in_data_file_path[i], list_scores[i]))

        print("==========================================================")      
        print("TOTAL SCORE: {}".format(total_score))
        print("==========================================================")        
    else:
        test_on_one_file(_path_to_file, _path_to_output)