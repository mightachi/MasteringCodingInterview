"""
import random


class ListNode:
    __slots__ = ('val', 'next', 'down')

    def __init__(self, val):
        self.val = val
        self.next = None
        self.down = None


class Skiplist:
    def __init__(self):
        # sentinel nodes to keep code simple
        node = ListNode(float('-inf'))
        node.next = ListNode(float('inf'))
        self.levels = [node]

    def search(self, target: int) -> bool:
        level = self.levels[-1]
        while level:
            node = level
            while node.next.val < target:
                node = node.next
            if node.next.val == target:
                return True
            level = node.down
        return False

    def add(self, num: int) -> None:
        stack = []
        level = self.levels[-1]
        while level:
            node = level
            while node.next.val < num:
                node = node.next
            stack.append(node)
            level = node.down

        heads = True
        down = None
        while stack and heads:
            prev = stack.pop()
            node = ListNode(num)
            node.next = prev.next
            node.down = down
            prev.next = node
            down = node
            # flip a coin to stop or continue with the next level
            heads = random.randint(0, 1)

        # add a new level if we got to the top with heads
        if not stack and heads:
            node = ListNode(float('-inf'))
            node.next = ListNode(num)
            node.down = self.levels[-1]
            node.next.next = ListNode(float('inf'))
            node.next.down = down
            self.levels.append(node)

    def erase(self, num: int) -> bool:
        stack = []
        level = self.levels[-1]
        while level:
            node = level
            while node.next.val < num:
                node = node.next
            if node.next.val == num:
                stack.append(node)
            level = node.down

        if not stack:
            return False

        for node in stack:
            node.next = node.next.next

        # remove the top level if it's empty
        while len(self.levels) > 1 and self.levels[-1].next.next is None:
            self.levels.pop()

        return True
"""



import random

class ListNode:
    def __init__(self, val=0, right=None, down=None):
        self.val = val
        self.right = right
        self.down = down

class Skiplist:
    def __init__(self):
        self.head = ListNode(float('-inf'))
        self.maxLevel = 1

    def search(self, target: int) -> bool:
        curr = self.head
        while curr:
            while curr.right and curr.right.val < target:
                curr = curr.right
            if curr.right and curr.right.val == target:
                return True
            curr = curr.down
        return False

    def add(self, num: int) -> None:
        level = 1
        while random.random() < 0.5:
            level += 1

        if level > self.maxLevel:
            self.addLevel()
            self.maxLevel = level

        curr = self.head
        node = ListNode(num)
        while curr:
            while curr.right and curr.right.val < num:
                curr = curr.right
            node.right = curr.right
            curr.right = node
            node = ListNode(num, None, node)
            curr = curr.down

    def erase(self, num: int) -> bool:
        found = False
        curr = self.head
        while curr:
            while curr.right and curr.right.val < num:
                curr = curr.right
            if curr.right and curr.right.val == num:
                curr.right = curr.right.right
                found = True
            curr = curr.down
        return found

    def addLevel(self):
        newHead = ListNode(float('-inf'), self.head)
        self.head = newHead

obj = Skiplist()
obj.add(10)
obj.add(5)
obj.add(30)
param_1 = obj.search(5)
obj.add(29)
param_3 = obj.erase(5)
print(param_1,param_3)