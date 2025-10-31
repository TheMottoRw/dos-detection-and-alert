import threading

class Producer:
    def __init__(self, semaphore_count=1):
        self._items = []
        self._sem = threading.Semaphore(semaphore_count)

    def add(self, items_new: list):
        self._sem.acquire()
        for item in items_new:
            matches = [m for m in self._items if m['site_name'] == item['site_name']]
            if len(matches) > 0:
                continue
            if item['priority'] == 5:
                self._items.insert(0, item)
            else:
                self._items.append(item)
        self._sem.release()
        return len(self._items)

    def consume(self, count=1):
        self._sem.acquire()
        if len(self._items) == 0:
            self._sem.release()
            return None

        last = count
        if count > len(self._items):
            count = len(self._items)
            last -= 1
        selection = self._items[:count]
        self._items = self._items[last:]
        self._sem.release()
        return selection
