import threading
from api.webmonitor.webchecker import verify_domains
from api.webmonitor.producer import Producer  # Assuming Producer is defined here

def main(worker_count: int = 2):
    # Create an instance of Producer
    producer = Producer()

    # Start domain verification workers
    workers = []
    for _ in range(max(1, worker_count)):
        t = threading.Thread(target=verify_domains, args=(producer,), daemon=True)
        t.start()
        workers.append(t)

    # Keep the main thread alive
    for t in workers:
        t.join()

if __name__ == "__main__":
    main()