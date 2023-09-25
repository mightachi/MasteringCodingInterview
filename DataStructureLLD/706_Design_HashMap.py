'''https://leetcode.com/problems/design-hashmap/description/

What is hashmap?
Hashing is a technique or process of mapping keys, and values into the hash table by using a hash function. It is done for faster access to elements.

Components of Hashing
There are majorly three components of hashing:

Key: A Key can be anything string or integer which is fed as input in the hash function the technique that determines an index or location for storage of an item 
      in a data structure. 
Hash Function: The hash function receives the input key and returns the index of an element in an array called a hash table. The index is known as the hash index.
Hash Table: Hash table is a data structure that maps keys to values using a special function called a hash function. Hash stores the data in an associative manner
        in an array where each data value has its own unique index.

What is Index Mapping?
Index Mapping (also known as Trivial Hashing) is a simple form of hashing where the data is directly mapped to an index in a hash table. The hash
function used in this method is typically the identity function, which maps the input data to itself. 

How to handle negative numbers? 
The idea is to use a 2D array of size hash[MAX+1][2]

What is Collision? 
The situation where a newly inserted key maps to an already occupied slot in the hash table is called collision.

What are the chances of collisions with the large table? 
An important observation is Birthday Paradox. With only 23 persons, the probability that two people have the same birthday is 50%.

How to handle Collisions? 
There are mainly two methods to handle collision: 

1. Separate Chaining 
---------------------
---------------------
The idea behind separate chaining is to implement the array as a linked list called a chain.

Advantages:
------------
1. Simple to implement. 
2. Hash table never fills up, we can always add more elements to the chain. 
3. Less sensitive to the hash function or load factors. 
4. It is mostly used when it is unknown how many and how frequently keys may be inserted or deleted. 

Disadvantages: 
--------------
1. The cache performance of chaining is not good as keys are stored using a linked list. Open addressing provides better cache performance as everything is stored in the same table. 
2. Wastage of Space (Some Parts of the hash table are never used) 
3. If the chain becomes long, then search time can become O(n) in the worst case
4. Uses extra space for links

Performance of Chaining: 
--------------------------
Performance of hashing can be evaluated under the assumption that each key is equally likely to be hashed to any slot of the table (simple uniform hashing).  

m = Number of slots in hash table
n = Number of keys to be inserted in hash table

Load factor α = n/m
Expected time to search = O(1 + α)
Expected time to delete = O(1 + α)

Time to insert = O(1)
Time complexity of search insert and delete is O(1) if  α is O(1)

2. Open Addressing 
-------------------
-------------------
In Open Addressing, all elements are stored in the hash table itself. So at any point, the size of the table must be greater than or equal to the total number of keys 
(Note that we can increase table size by copying old data if needed). This approach is also known as closed hashing. This entire procedure is based upon probing. 
We will understand the types of probing ahead:

Insert(k): Keep probing until an empty slot is found. Once an empty slot is found, insert k. 
Search(k): Keep probing until the slot’s key doesn’t become equal to k or an empty slot is reached. 
Delete(k): Delete operation is interesting. If we simply delete a key, then the search may fail. So slots of deleted keys are marked specially as “deleted”. 
The insert can insert an item in a deleted slot, but the search doesn’t stop at a deleted slot. 

Different ways of Open Addressing:
----------------------------------
1. Linear Probing: 
Let hash(x) be the slot index computed using a hash function and S be the table size 

If slot hash(x) % S is full, then we try (hash(x) + 1) % S
If (hash(x) + 1) % S is also full, then we try (hash(x) + 2) % S
If (hash(x) + 2) % S is also full, then we try (hash(x) + 3) % S 

Challenges in Linear Probing :
------------------------------
Primary Clustering: One of the problems with linear probing is Primary clustering, many consecutive elements form groups and it starts taking time to find a free 
                    slot or to search for an element.  
Secondary Clustering: Secondary clustering is less severe, two records only have the same collision chain (Probe Sequence) if their initial position is the same.

2. Quadratic Probing:
--------------------
let hash(x) be the slot index computed using hash function.  

If slot hash(x) % S is full, then we try (hash(x) + 1*1) % S
If (hash(x) + 1*1) % S is also full, then we try (hash(x) + 2*2) % S
If (hash(x) + 2*2) % S is also full, then we try (hash(x) + 3*3) % S

3. Double Hashing
------------------
let hash(x) be the slot index computed using hash function.  

If slot hash(x) % S is full, then we try (hash(x) + 1*hash2(x)) % S
If (hash(x) + 1*hash2(x)) % S is also full, then we try (hash(x) + 2*hash2(x)) % S
If (hash(x) + 2*hash2(x)) % S is also full, then we try (hash(x) + 3*hash2(x)) % S

Performance of Open Addressing: 
--------------------------------
Like Chaining, the performance of hashing can be evaluated under the assumption that each key is equally likely to be hashed to any slot of the table (simple uniform hashing) 

m = Number of slots in the hash table

n = Number of keys to be inserted in the hash table

 Load factor α = n/m  ( < 1 )

Expected time to search/insert/delete < 1/(1 – α) 

So Search, Insert and Delete take (1/(1 – α)) time

Difference between Separate Chaining and Open Addressing
--------------------------------------------------------
1. Chaining is Simpler to implement but Open Addressing requires more computation.
2. In chaining, Hash table never fills up, we can always add more elements to chain. but In open addressing, table may become full.
3. Chaining is Less sensitive to the hash function or load factors. but Open addressing requires extra care to avoid clustering and load factor.
4. Chaining is mostly used when it is unknown how many and how frequently keys may be inserted or deleted. but Open addressing is used when the frequency and number of keys is known.
5. Cache performance of chaining is not good as keys are stored using linked list. but Open addressing provides better cache performance as everything is stored in the same table.
6. Wastage of Space (Some Parts of hash table in chaining are never used). but In Open addressing, a slot can be used even if an input doesn’t map to it.
7. Chaining uses extra space for links. but No links in Open addressing

What is rehashing?
Rehashing is the process of increasing the size of a hashmap and redistributing the elements to new buckets based on their new hash values.

Why rehashing?
Rehashing is needed in a hashmap to prevent collision and to maintain the efficiency of the data structure.

Problem
-------
-------
Design a HashMap without using any built-in hash table libraries.

Implement the MyHashMap class:

MyHashMap() initializes the object with an empty map.
void put(int key, int value) inserts a (key, value) pair into the HashMap. If the key already exists in the map, update the corresponding value.
int get(int key) returns the value to which the specified key is mapped, or -1 if this map contains no mapping for the key.
void remove(key) removes the key and its corresponding value if the map contains the mapping for the key.
 

Example 1:

Input
["MyHashMap", "put", "put", "get", "get", "put", "get", "remove", "get"]
[[], [1, 1], [2, 2], [1], [3], [2, 1], [2], [2], [2]]
Output
[null, null, null, 1, -1, null, 1, null, -1]

Explanation
MyHashMap myHashMap = new MyHashMap();
myHashMap.put(1, 1); // The map is now [[1,1]]
myHashMap.put(2, 2); // The map is now [[1,1], [2,2]]
myHashMap.get(1);    // return 1, The map is now [[1,1], [2,2]]
myHashMap.get(3);    // return -1 (i.e., not found), The map is now [[1,1], [2,2]]
myHashMap.put(2, 1); // The map is now [[1,1], [2,1]] (i.e., update the existing value)
myHashMap.get(2);    // return 1, The map is now [[1,1], [2,1]]
myHashMap.remove(2); // remove the mapping for 2, The map is now [[1,1]]
myHashMap.get(2);    // return -1 (i.e., not found), The map is now [[1,1]]

'''

class MyHashMap:

    def __init__(self):
        self.size = 1000
        self.buckets = [None] * self.size

    def put(self, key: int, value: int) -> None:
        index = self.hash_function(key)
        if not self.buckets[index]:
            self.buckets[index] = []
        for i in range(len(self.buckets[index])):
            if self.buckets[index][i][0] == key:
                self.buckets[index][i] = (key, value)
                return
        self.buckets[index].append((key, value))

    def get(self, key: int) -> int:
        index = self.hash_function(key)
        if not self.buckets[index]:
            return -1
        for k, v in self.buckets[index]:
            if k == key:
                return v
        return -1

    def remove(self, key: int) -> None:
        index = self.hash_function(key)
        if not self.buckets[index]:
            return
        for i in range(len(self.buckets[index])):
            if self.buckets[index][i][0] == key:
                del self.buckets[index][i]
                return

    def hash_function(self, key: int) -> int:
        return key % self.size

        


# Your MyHashMap object will be instantiated and called as such:
# obj = MyHashMap()
# obj.put(key,value)
# param_2 = obj.get(key)
# obj.remove(key)
