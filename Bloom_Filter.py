from bitarray import bitarray
import mmh3

class BloomFilter:

    def __init__(self, size, hash_count):
        self.size = size
        self.hash_count = hash_count
        self.bit_array = bitarray(size)
        self.bit_array.setall(0)

    def add(self, string):
        for seed in xrange(self.hash_count):
            result = mmh3.hash(string, seed) % self.size
            self.bit_array[result] = 1

    def lookup(self, string):
        for seed in xrange(self.hash_count):
            try:
                result = mmh3.hash(string, seed) % self.size
                if self.bit_array[result] == 0:
                    return 0
            except:
                return 1
        return 1

'''bf = BloomFilter(500000, 7)

lines = open("bloomtest.txt").read().splitlines()
for line in lines:
    bf.add(line)

print bf.lookup("746")
print bf.lookup("Sun")
print bf.lookup("2015")
print bf.lookup("3")'''
