import argparse
import csv
from collections import deque


class Request:
    def __init__(self, arrival_time, path, processing_time):
        self.arrival_time = int(arrival_time)
        self.path = path
        self.processing_time = int(processing_time)
        self.start_time = None

    def wait_time(self):
        return self.start_time - self.arrival_time


class Server:
    def __init__(self):
        self.current_request = None
        self.time_remaining = 0

    def is_busy(self):
        return self.time_remaining > 0

    def tick(self):
        if self.time_remaining > 0:
            self.time_remaining -= 1
            if self.time_remaining == 0:
                self.current_request = None

    def start_next(self, request, current_time):
        request.start_time = current_time
        self.current_request = request
        self.time_remaining = request.processing_time


def simulateOneServer(filename):
    requests = []

    with open(filename, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            requests.append(Request(row[0], row[1], row[2]))

    queue = deque()
    server = Server()
    wait_times = []

    current_time = 0
    request_index = 0
    total_requests = len(requests)

    while request_index < total_requests or server.is_busy() or queue:

        # Add arriving requests to queue
        while request_index < total_requests and requests[request_index].arrival_time == current_time:
            queue.append(requests[request_index])
            request_index += 1

        # If server idle and queue not empty, process next request
        if not server.is_busy() and queue:
            next_request = queue.popleft()
            server.start_next(next_request, current_time)
            wait_times.append(next_request.wait_time())

        server.tick()
        current_time += 1

    average_wait = sum(wait_times) / len(wait_times)
    print(f"Average wait time (1 server): {average_wait:.2f} seconds")
    return average_wait


def simulateManyServers(filename, num_servers):
    requests = []

    with open(filename, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            requests.append(Request(row[0], row[1], row[2]))

    servers = [Server() for _ in range(num_servers)]
    queues = [deque() for _ in range(num_servers)]
    wait_times = []

    current_time = 0
    request_index = 0
    total_requests = len(requests)
    round_robin = 0

    while request_index < total_requests or any(s.is_busy() for s in servers) or any(queues):

        # Add arriving requests
        while request_index < total_requests and requests[request_index].arrival_time == current_time:
            queues[round_robin].append(requests[request_index])
            request_index += 1
            round_robin = (round_robin + 1) % num_servers

        for i in range(num_servers):
            if not servers[i].is_busy() and queues[i]:
                next_request = queues[i].popleft()
                servers[i].start_next(next_request, current_time)
                wait_times.append(next_request.wait_time())

            servers[i].tick()

        current_time += 1

    average_wait = sum(wait_times) / len(wait_times)
    print(f"Average wait time ({num_servers} servers): {average_wait:.2f} seconds")
    return average_wait


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', required=True)
    parser.add_argument('--servers', type=int)

    args = parser.parse_args()

    if args.servers:
        simulateManyServers(args.file, args.servers)
    else:
        simulateOneServer(args.file)


if __name__ == "__main__":
    main()
