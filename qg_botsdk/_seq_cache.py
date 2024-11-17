class SeqCache:
    def __init__(self, size: int = 100):
        self.size = size
        self.cache = [None] * size
        self.ptr = 0
        self.cache_set = set()

    def __del_cache(self, index: int):
        if self.cache[index] is None:
            return
        self.cache_set.remove(self.cache[index])
        self.cache[index] = None

    def add(self, seq: int):
        self.__del_cache(self.ptr)
        self.cache[self.ptr] = seq
        self.cache_set.add(seq)
        self.ptr = (self.ptr + 1) % self.size

    def add_with_checking(self, seq: int) -> bool:
        if seq in self.cache_set:
            return False
        self.add(seq)
        return True
