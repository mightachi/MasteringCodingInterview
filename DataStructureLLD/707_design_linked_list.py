'''
Problem: https://leetcode.com/problems/design-linked-list/
'''
class Node:
    
    def __init__(self, data):
        self.data = data
        self.next = None

class MyLinkedList:

    def __init__(self):
        self.head = None

    def get(self, index: int) -> int:
        node_at_index = self.head
        if self.head == None:
            return -1
        elif index < 0:
            return -1
        else:
            while index > 0 and node_at_index.next != None:
                node_at_index = node_at_index.next
                index -= 1
            if index != 0:
                return -1
            else:  
                return node_at_index.data
        


    def addAtHead(self, val: int) -> None:
        temp = self.head
        self.head = Node(val)
        self.head.next = temp

    def addAtTail(self, val: int) -> None:
        node_at_tail = self.head
        while node_at_tail.next != None:
            node_at_tail = node_at_tail.next
        node_at_tail.next = Node(val)

    def addAtIndex(self, index: int, val: int) -> None:
        node_at_index = self.head
        node_at_prev_index = None
        if index >= 0:
            while index > 0 and node_at_index.next != None:
                node_at_prev_index = node_at_index
                node_at_index = node_at_index.next
                index -= 1
            if index <= 1:
                node_at_prev_index.next = Node(val)
                node_at_prev_index.next.next = node_at_index
            else:
                return None
        else:
            return None

    def deleteAtIndex(self, index: int) -> None:
        node_at_index = self.head
        if index >=0:
            node_at_prev_index = None
            while index > 0 and node_at_index.next != None:
                node_at_prev_index = node_at_index
                node_at_index = node_at_index.next
                index -= 1
            if index != 0:
                return None
            elif node_at_prev_index == None:
                self.head = self.head.next
            else:  
                node_at_prev_index.next = node_at_index.next
        else:
            return None

'''
Test Cases:
Case 1:
["MyLinkedList","addAtHead","addAtHead","addAtHead","addAtIndex","deleteAtIndex","addAtHead","addAtTail","get","addAtHead","addAtIndex","addAtHead"]
[[],[7],[2],[1],[3,0],[2],[6],[4],[4],[4],[5,0],[6]]
'''

# obj = MyLinkedList()
# obj.addAtHead(7)
# obj.addAtHead(2)
# obj.addAtHead(1)
# obj.addAtIndex(3,0)
# obj.deleteAtIndex(2)
# obj.addAtHead(6)
# obj.addAtTail(4)
# param_1 = obj.get(4)
# obj.addAtHead(4)
# obj.addAtIndex(5,0)
# obj.addAtHead(6)

'''
Case 2:
["MyLinkedList","addAtHead","addAtTail","addAtIndex","get","deleteAtIndex","get"]
[[],[1],[3],[1,2],[1],[0],[0]]
'''

# obj = MyLinkedList()
# obj.addAtHead(1)
# obj.addAtTail(3)
# obj.addAtIndex(1,2)
# param_1 = obj.get(1)
# obj.deleteAtIndex(0)
# param_1 = obj.get(0)

'''
Case 3:
["MyLinkedList","addAtIndex","addAtIndex","addAtIndex","get"]
[[],[0,10],[0,20],[1,30],[0]]
'''
