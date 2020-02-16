class Endpoint:
    id = 0
    by_id = {}
    def __init__(self, dc_latency):
        self.caches = set()  # The set of caches connected to this endpoint
        self.cache_latency = {} # Latency between each connected cache and endpoint
        self.data_center_latency = dc_latency

        self.id = Endpoint.id
        Endpoint.by_id[self.id] = self
        Endpoint.id += 1

    def __hash__(self):
        return self.id
