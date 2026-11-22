import random


def random_requests(num_keys, num_requests, seed=42):
    rng = random.Random(seed)
    requests = []
    for _ in range(num_requests):
        requests.append(rng.randrange(num_keys))
    return requests


def make_weights(num_keys, alpha):
    weights = []
    for rank in range(1, num_keys + 1):
        weights.append(1 / (rank ** alpha))
    return weights


def zipf_requests(num_keys, num_requests, alpha=1.0, seed=42):
    rng = random.Random(seed)
    keys = list(range(num_keys))
    weights = make_weights(num_keys, alpha)
    return rng.choices(keys, weights=weights, k=num_requests)


def shifting_zipf_requests(num_keys, num_requests, phases=4, alpha=1.0, seed=42):
    rng = random.Random(seed)
    weights = make_weights(num_keys, alpha)
    per_phase = num_requests // phases

    requests = []
    for _ in range(phases):
        keys = list(range(num_keys))
        rng.shuffle(keys)
        requests = requests + rng.choices(keys, weights=weights, k=per_phase)
    return requests


def load_trace(path):
    keys = []
    with open(path) as f:
        next(f)
        for line in f:
            parts = line.split(",")
            keys.append(parts[1].strip())
    return keys
