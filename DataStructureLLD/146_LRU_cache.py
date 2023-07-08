'''
https://leetcode.com/problems/lru-cache/description/
'''

class ListNode:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = {}
        self.head = ListNode(0, 0)  # dummy head
        self.tail = ListNode(0, 0)  # dummy tail
        self.head.next = self.tail
        self.tail.prev = self.head

    def get(self, key):
        if key in self.cache:
            node = self.cache[key]
            self._remove(node)
            self._add(node)
            return node.value
        return -1

    def put(self, key, value):
        if key in self.cache:
            node = self.cache[key]
            self._remove(node)
        elif len(self.cache) == self.capacity:
            node = self.tail.prev
            self._remove(node)
            del self.cache[node.key]

        node = ListNode(key, value)
        self.cache[key] = node
        self._add(node)

    def _remove(self, node):
        prev_node = node.prev
        next_node = node.next
        prev_node.next = next_node
        next_node.prev = prev_node

    def _add(self, node):
        next_node = self.head.next
        self.head.next = node
        node.prev = self.head
        node.next = next_node
        next_node.prev = node
