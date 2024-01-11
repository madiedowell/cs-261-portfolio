# Name: Madison Dowell
# OSU Email: dowellma@oregonstate.edu
# Course: CS261 - Data Structures
# Assignment: Assignment 6
# Due Date: August 15, 11:59 pm
# Description: This is a HashMap class that includes the following methods: put(), get(), remove(), contains_key(),
# clear(), empty_buckets(), resize_table(), table_load(), get_keys(), and find_mode().
# This class uses seperate chaining to handle collisions

from a6_include import DynamicArray, LinkedList, hash_function_1, hash_function_2


class HashMap:
    def __init__(
        self, capacity: int = 11, function: callable = hash_function_1
    ) -> None:
        """
        Initialize new HashMap that uses
        separate chaining for collision resolution
        DO NOT CHANGE THIS METHOD IN ANY WAY
        """
        self._buckets = DynamicArray()

        # capacity must be a prime number
        self._capacity = self._next_prime(capacity)
        for _ in range(self._capacity):
            self._buckets.append(LinkedList())

        self._hash_function = function
        self._size = 0

    def __str__(self) -> str:
        """
        Override string method to provide more readable output
        DO NOT CHANGE THIS METHOD IN ANY WAY
        """
        out = ""
        for i in range(self._buckets.length()):
            out += str(i) + ": " + str(self._buckets[i]) + "\n"
        return out

    def _next_prime(self, capacity: int) -> int:
        """
        Increment from given number and the find the closest prime number
        DO NOT CHANGE THIS METHOD IN ANY WAY
        """
        if capacity % 2 == 0:
            capacity += 1

        while not self._is_prime(capacity):
            capacity += 2

        return capacity

    @staticmethod
    def _is_prime(capacity: int) -> bool:
        """
        Determine if given integer is a prime number and return boolean
        DO NOT CHANGE THIS METHOD IN ANY WAY
        """
        if capacity == 2 or capacity == 3:
            return True

        if capacity == 1 or capacity % 2 == 0:
            return False

        factor = 3
        while factor**2 <= capacity:
            if capacity % factor == 0:
                return False
            factor += 2

        return True

    def get_size(self) -> int:
        """
        Return size of map
        DO NOT CHANGE THIS METHOD IN ANY WAY
        """
        return self._size

    def get_capacity(self) -> int:
        """
        Return capacity of map
        DO NOT CHANGE THIS METHOD IN ANY WAY
        """
        return self._capacity

    # ------------------------------------------------------------------ #

    # Additional helper functions

    def ensure_capacity_is_prime(self, new_capacity: int) -> int:
        '''
        Ensures that the given new capacity is a prime number

        :param new_capacity: The capacity to be validated and adjusted if necessary

        :return: The new capacity
        '''
        if not self._is_prime(new_capacity):
            #If not prime, find the next prime number and set it to new capacity
            new_capacity = self._next_prime(new_capacity)

        return new_capacity

    def get_new_capacity(self, new_capacity: int) -> int:
        '''
        Calculates and returns the adjusted capacity based on the desired new capacity while maintaining a balanced load factor

        :param new_capacity: The desired initial capacity

        :return: An adjusted capacity that is a prime number and maintains a balanced load factor
        '''
        #Ensure the initial capacity is a prime number or the next prime number
        new_capacity = self.ensure_capacity_is_prime(new_capacity)
        self._capacity = new_capacity

        #Calculate the initial load factor of the table
        load_factor = self.table_load()

        #Continuously adjust the capacity to achieve a load factor less than or equal to 1
        while load_factor > 1:
            new_capacity *= 2
            new_capacity = self.ensure_capacity_is_prime(new_capacity)
            self._capacity = new_capacity
            load_factor = self.table_load()

        return new_capacity

    def get_bucket_index(self, key: str) -> int:
        '''
        Calculates the bucket index for a given key using a hash function and the bucket length

        :param key: The key for which the bucket index needs to be calculated

        :return: The bucket index for the given key
        '''

        hash_code = self._hash_function(str(key))
        index = hash_code % self._buckets.length()

        return index

    def insert_node(self, bucket: LinkedList, key: str, value: object) -> None:
        '''
        Inserts a key-value pair into the specified bucket of the hash table

        :param bucket: The linked list/bucket where the key-value pair will be inserted

        :param key: The key to be inserted

        :param value: The value to be inserted

        :return: None
        '''
        LinkedList.insert(bucket, key, value)
        self._size += 1

    def update_value(self, index: int, key: str, value: object) -> bool:
        '''
        Updates the value associated with a given key in the specified bucket of the hash table

        :param index: The index of the bucket in which the value is to be updated

        :param key: The key for the value that needs to be updated

        :param value: The new value to be associated with the key

        :return: True if the update is successful, False if the key is not found
        '''
        #Get the bucket at the specified index
        bucket = self._buckets[index]

        #Initialize a pointer to the head of the buckets linked list
        node = bucket._head


        key_exists = False
        i = 0

        #Iterate through the linked list
        while i < bucket.length() and key_exists is False:
            if node.key == key:
                #Update value if key is found
                node.value = value
                key_exists = True
            #Move to the next node in the linked list if the key is not found
            next_node = node.next
            node = next_node
            i += 1

        return key_exists

    def process_key_and_value(self, key: str, value: object) -> None:
        '''
        Processes a key-value pair by updating an existing key's value or inserting a new key-value pair into the hash table.

        :param key: The key to be processed

        :param value: The value to be associated with the key

        :return: None
        '''
        bucket_index = self.get_bucket_index(key)
        bucket = self._buckets[bucket_index]

        #If bucket is empty, insert key-value pair
        if bucket.length() == 0:
            self.insert_node(bucket, key, value)
        else:
            #If bucket is not empty, try to update value
            key_exists = self.update_value(bucket_index, key, value)

            #If the key is not found in the bucket, insert the key-value pair
            if not key_exists:
                self.insert_node(bucket, key, value)

    def get_head_node(self, key: str) -> object:
        '''
        Retrieves the head node of the linked list in the bucket corresponding to the given key

        :param key: The key for which the head node needs to be retrieved

        :return: The head node
        '''

        index = self.get_bucket_index(key)
        bucket = self._buckets[index]
        node = None

        if bucket.length != 0:
            node = bucket._head

        return node

    # ------------------------------------------------------------------ #

    def put(self, key: str, value: object) -> None:
        '''
        Inserts a key-value pair into the hash table, resizing the table if needed

        :param key: The key to be inserted

        :param value: The value associated with the key

        :return: None
        '''
        load_factor = self.table_load()

        #If load factor is greater than or equal to 1, double the capacity and resize the table
        if load_factor >= 1:
            new_capacity = self._capacity * 2
            self.resize_table(new_capacity)

        bucket_index = self.get_bucket_index(key)

        #If index is out of range, double the capacity and resize the table
        if bucket_index > self._capacity - 1:
            new_capacity = self._capacity * 2
            self.resize_table(new_capacity)

        #Process the key and value pair by inserting or updating them in the hash table
        self.process_key_and_value(key, value)

    def empty_buckets(self) -> int:
        '''
        Counts and returns the number of empty buckets in the hash table

        :return: The count of empty buckets
        '''
        num_empty_buckets = 0

        #Iterate through all the buckets in the hash table and check if the current bucket is empty
        for i in range(0, self.get_capacity()):
            if self._buckets[i].length() == 0:
                num_empty_buckets += 1

        return num_empty_buckets

    def table_load(self) -> float:
        '''
        Calculates and returns the load factor of the hash table

        :return:The load factor as a floating point number
        '''
        num_buckets = self.get_capacity()
        num_elements = self.get_size()
        load_factor = num_elements / num_buckets

        return load_factor

    def clear(self) -> None:
        '''
        Clear the hash table by removing all elements and resetting its internal state

        :return:None
        '''
        #Create a new DynamicArray to store the buckets of the hash table
        self._buckets = DynamicArray()

        #Initialize each bucket as an empty list
        for _ in range(self._capacity):
            self._buckets.append(LinkedList())

        #Reset the size of the hash table to zero
        self._size = 0

    def resize_table(self, new_capacity: int) -> None:
        '''
        Resize the hash table to the specified new capacity, rehashing all elements

        :param new_capacity: The new capacity for the hash table after resizing

        :return:None
        '''
        if new_capacity >= 1:
            #Update capacity of hash table
            self._capacity = new_capacity

            #Calculate the new capacity based on load factor if needed
            new_capacity = self.get_new_capacity(new_capacity)

            #Save reference to the old hash table
            temp_table = self._buckets

            self.clear()

            #Iterate through each bucket in the old hash table
            for i in range(0, temp_table.length()):
                temp_bucket = temp_table[i]

                #Process each element in the bucket
                if temp_bucket.length() != 0:
                    node = temp_bucket._head
                    while node:
                        key = node.key
                        value = node.value
                        #Rehash the key-value pair and insert it into the resized hash table
                        self.process_key_and_value(key, value)
                        next_node = node.next
                        node = next_node

    def get(self, key: str) -> object:
        '''
        Retrieve the value associated with the given key from the hash table

        :param key: The key from which to retrieve the associated value

        :return: The value associated with the key if found, otherwise None
        '''
        if self._buckets.length() > 0:
            #Get the head node of the linked list in the appropriate bucket
            node = self.get_head_node(key)

            #Traverse the linked list to find the matching key
            while node:
                current_key = node.key
                if current_key == key:
                    value = node.value
                    node = None
                    return value
                else:
                    next_node = node.next
                    node = next_node

        return None

    def contains_key(self, key: str) -> bool:
        '''
        Check if the hash table contains the specified key

        :param key: The key to check for in the hash table

        :return: True if the key is found, False otherwise
        '''
        if self._buckets.length() > 0:
            #Get the head node of the linked list in the appropriate bucket
            node = self.get_head_node(key)

            #Traverse the linked list to check if the key exists
            while node:
                current_key = node.key
                if current_key == key:
                    node = None
                    return True
                else:
                    next_node = node.next
                    node = next_node

        return False

    def remove(self, key: str) -> None:
        '''
        Removes the key-value pair associated with the specified key from the hash table

        :param key: The key of the key-value pair to remove from the hash table

        :return: None
        '''
        if self._buckets.length() > 0:
            #Calculate the index of the bucket where the key may be present
            index = self.get_bucket_index(key)

            #Get the bucket at the calculated index
            bucket = self._buckets[index]

            #Remove the key-value pair from the linked list within the bucket
            removed = LinkedList.remove(bucket, key)
            if removed:
                self._size -= 1

    def get_keys_and_values(self) -> DynamicArray:
        '''
        Retrieves all key-value pairs from the hash table and return them as a DynamicArray

        :return: A DynamicArray containing all key-value pairs from the hash table
        '''
        #Create a new DynamicArray to store the key-value pairs
        da = DynamicArray()

        #Iterate through each bucket in the hash table
        for i in range(0, self._buckets.length()):
            bucket = self._buckets[i]

            #Collect key-value pairs from the linked list in the bucket
            if bucket.length() != 0:
                node = bucket._head
                while node:
                    key = node.key
                    value = node.value
                    key_value_pair = (key, value)
                    da.append(key_value_pair)
                    #Move to the next node
                    next_node = node.next
                    node = next_node

        return da


def find_mode(da: DynamicArray) -> tuple[DynamicArray, int]:
    '''
    Find the mode(s) and frequency in a DynamicArray of values

    :param da: The DynamicArray containing the values for which to find the mode

    :return: A tuple containing a DynamicArray of mode(s) and their frequency
    '''
    mode = DynamicArray()
    frequency = 0
    max_frequency = 0

    #Create a hash map to store value-frequency pairs
    map = HashMap(53, hash_function_2)

    #Iterate through each value in the input DynamicArray
    for i in range(0, da.length()):
        key = da[i]

        #Calculate the bucket index using the hash map's hash function
        index = map.get_bucket_index(key)

        #Check if the bucket contains elements
        if map._buckets[index].length() != 0:
            node = map.get_head_node(key)

            #Search for the key in the linked list of the bucket
            while node:
                if node.key == key:
                    current_frequency = node.value
                    frequency = current_frequency + 1
                    node = None
                else:
                    next_node = node.next
                    node = next_node
                    frequency = 1
        else:
            frequency = 1

        #Update the hash map with the value-frequency pair
        map.put(key, frequency)

        #Update the mode(s) and max frequency if needed
        if frequency > max_frequency:
            max_frequency = frequency
            mode = DynamicArray()
            mode.append(key)
        elif frequency == max_frequency:
            mode.append(key)

    #Set the final frequency value and return the mode(s) and frequency
    frequency = max_frequency
    return mode, frequency


# ------------------- BASIC TESTING ---------------------------------------- #

if __name__ == "__main__":
    print("\nPDF - put example 1")
    print("-------------------")
    m = HashMap(53, hash_function_1)
    for i in range(150):
        m.put("str" + str(i), i * 100)
        if i % 25 == 24:
            print(
                m.empty_buckets(),
                round(m.table_load(), 2),
                m.get_size(),
                m.get_capacity(),
            )

    print("\nPDF - put example 2")
    print("-------------------")
    m = HashMap(41, hash_function_2)
    for i in range(50):
        m.put("str" + str(i // 3), i * 100)
        if i % 10 == 9:
            print(
                m.empty_buckets(),
                round(m.table_load(), 2),
                m.get_size(),
                m.get_capacity(),
            )

    print("\nPDF - empty_buckets example 1")
    print("-----------------------------")
    m = HashMap(101, hash_function_1)
    print(m.empty_buckets(), m.get_size(), m.get_capacity())
    m.put("key1", 10)
    print(m.empty_buckets(), m.get_size(), m.get_capacity())
    m.put("key2", 20)
    print(m.empty_buckets(), m.get_size(), m.get_capacity())
    m.put("key1", 30)
    print(m.empty_buckets(), m.get_size(), m.get_capacity())
    m.put("key4", 40)
    print(m.empty_buckets(), m.get_size(), m.get_capacity())

    print("\nPDF - empty_buckets example 2")
    print("-----------------------------")
    m = HashMap(53, hash_function_1)
    for i in range(150):
        m.put("key" + str(i), i * 100)
        if i % 30 == 0:
            print(m.empty_buckets(), m.get_size(), m.get_capacity())

    print("\nPDF - table_load example 1")
    print("--------------------------")
    m = HashMap(101, hash_function_1)
    print(round(m.table_load(), 2))
    m.put("key1", 10)
    print(round(m.table_load(), 2))
    m.put("key2", 20)
    print(round(m.table_load(), 2))
    m.put("key1", 30)
    print(round(m.table_load(), 2))

    print("\nPDF - table_load example 2")
    print("--------------------------")
    m = HashMap(53, hash_function_1)
    for i in range(50):
        m.put("key" + str(i), i * 100)
        if i % 10 == 0:
            print(round(m.table_load(), 2), m.get_size(), m.get_capacity())

    print("\nPDF - clear example 1")
    print("---------------------")
    m = HashMap(101, hash_function_1)
    print(m.get_size(), m.get_capacity())
    m.put("key1", 10)
    m.put("key2", 20)
    m.put("key1", 30)
    print(m.get_size(), m.get_capacity())
    m.clear()
    print(m.get_size(), m.get_capacity())

    print("\nPDF - clear example 2")
    print("---------------------")
    m = HashMap(53, hash_function_1)
    print(m.get_size(), m.get_capacity())
    m.put("key1", 10)
    print(m.get_size(), m.get_capacity())
    m.put("key2", 20)
    print(m.get_size(), m.get_capacity())
    m.resize_table(100)
    print(m.get_size(), m.get_capacity())
    m.clear()
    print(m.get_size(), m.get_capacity())

    print("\nPDF - resize example 1")
    print("----------------------")
    m = HashMap(20, hash_function_1)
    m.put("key1", 10)
    print(m.get_size(), m.get_capacity(), m.get("key1"), m.contains_key("key1"))
    m.resize_table(30)
    print(m.get_size(), m.get_capacity(), m.get("key1"), m.contains_key("key1"))

    print("\nPDF - resize example 2")
    print("----------------------")
    m = HashMap(75, hash_function_2)
    keys = [i for i in range(1, 1000, 13)]
    for key in keys:
        m.put(str(key), key * 42)
    print(m.get_size(), m.get_capacity())

    for capacity in range(111, 1000, 117):
        m.resize_table(capacity)

        m.put("some key", "some value")
        result = m.contains_key("some key")
        m.remove("some key")

        for key in keys:
            # all inserted keys must be present
            result &= m.contains_key(str(key))
            # NOT inserted keys must be absent
            result &= not m.contains_key(str(key + 1))
        print(
            capacity, result, m.get_size(), m.get_capacity(), round(m.table_load(), 2)
        )

    print("\nPDF - get example 1")
    print("-------------------")
    m = HashMap(31, hash_function_1)
    print(m.get("key"))
    m.put("key1", 10)
    print(m.get("key1"))

    print("\nPDF - get example 2")
    print("-------------------")
    m = HashMap(151, hash_function_2)
    for i in range(200, 300, 7):
        m.put(str(i), i * 10)
    print(m.get_size(), m.get_capacity())
    for i in range(200, 300, 21):
        print(i, m.get(str(i)), m.get(str(i)) == i * 10)
        print(i + 1, m.get(str(i + 1)), m.get(str(i + 1)) == (i + 1) * 10)

    print("\nPDF - contains_key example 1")
    print("----------------------------")
    m = HashMap(53, hash_function_1)
    print(m.contains_key("key1"))
    m.put("key1", 10)
    m.put("key2", 20)
    m.put("key3", 30)
    print(m.contains_key("key1"))
    print(m.contains_key("key4"))
    print(m.contains_key("key2"))
    print(m.contains_key("key3"))
    m.remove("key3")
    print(m.contains_key("key3"))

    print("\nPDF - contains_key example 2")
    print("----------------------------")
    m = HashMap(79, hash_function_2)
    keys = [i for i in range(1, 1000, 20)]
    for key in keys:
        m.put(str(key), key * 42)
    print(m.get_size(), m.get_capacity())
    result = True
    for key in keys:
        # all inserted keys must be present
        result &= m.contains_key(str(key))
        # NOT inserted keys must be absent
        result &= not m.contains_key(str(key + 1))
    print(result)

    print("\nPDF - remove example 1")
    print("----------------------")
    m = HashMap(53, hash_function_1)
    print(m.get("key1"))
    m.put("key1", 10)
    print(m.get("key1"))
    m.remove("key1")
    print(m.get("key1"))
    m.remove("key4")

    print("\nPDF - get_keys_and_values example 1")
    print("------------------------")
    m = HashMap(11, hash_function_2)
    for i in range(1, 6):
        m.put(str(i), str(i * 10))
    print(m.get_keys_and_values())

    m.put("20", "200")
    m.remove("1")
    m.resize_table(2)
    print(m.get_keys_and_values())

    print("\nPDF - find_mode example 1")
    print("-----------------------------")
    da = DynamicArray(["apple", "apple", "grape", "melon", "peach"])
    mode, frequency = find_mode(da)
    print(f"Input: {da}\nMode : {mode}, Frequency: {frequency}")

    print("\nPDF - find_mode example 2")
    print("-----------------------------")
    test_cases = (
        [
            "Arch",
            "Manjaro",
            "Manjaro",
            "Mint",
            "Mint",
            "Mint",
            "Ubuntu",
            "Ubuntu",
            "Ubuntu",
        ],
        ["one", "two", "three", "four", "five"],
        ["2", "4", "2", "6", "8", "4", "1", "3", "4", "5", "7", "3", "3", "2"],
    )

    for case in test_cases:
        da = DynamicArray(case)
        mode, frequency = find_mode(da)
        print(f"Input: {da}\nMode : {mode}, Frequency: {frequency}\n")
