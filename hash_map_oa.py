# Name: Madison Dowell
# OSU Email: dowellma@oregonstate.edu
# Course: CS261 - Data Structures
# Assignment: Assignment 6
# Due Date: August 15, 11:59 pm
# Description: This is a HashMap class that includes the following methods: put(), get(), remove(), contains_key(),
# clear(), empty_buckets(), resize_table(), table_load(), get_keys(), and find_mode().
# This class uses open addressing with quadratic probing to handle collisions

from a6_include import (
    DynamicArray,
    DynamicArrayException,
    HashEntry,
    hash_function_1,
    hash_function_2,
)


class HashMapIterator:
    def __init__(self, map):
        self.map = map
        self.index = 0

    def __iter__(self):
        """
        This method makes the object iterable by return itself

        :return: Self
        """
        return self

    def __next__(self):
        """
        Retrieve the next non-tombstone bucket from the map

        :return:The next non-tombstone bucket from the map
        """
        # Iterate over the buckets of the map until the end is reached
        while self.index < self.map._buckets.length():
            bucket = self.map._buckets[self.index]
            self.index += 1

            if bucket is not None:
                if bucket.is_tombstone is not True:
                    return bucket

        raise StopIteration


class HashMap:
    def __init__(self, capacity: int, function) -> None:
        """
        Initialize new HashMap that uses
        quadratic probing for collision resolution
        DO NOT CHANGE THIS METHOD IN ANY WAY
        """
        self._buckets = DynamicArray()

        # capacity must be a prime number
        self._capacity = self._next_prime(capacity)
        for _ in range(self._capacity):
            self._buckets.append(None)

        self._hash_function = function
        self._size = 0

    def __iter__(self):
        return HashMapIterator(self)

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
        Increment from given number to find the closest prime number
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
        while factor ** 2 <= capacity:
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

    def get_hash_entry(self, key: str, value: object) -> object:
        """
        Creates and returns a HashEntry object containing the specified key and value

        :param key: The key to be associated with the HAshEntry

        :param value: The value to be associated with the HashEntry

        :return: A HashEntry object containing the specified key and value
        """
        return HashEntry(key, value)

    def ensure_capacity_is_prime(self, new_capacity: int) -> int:
        """
        Ensures that the given capacity is a prime number or the next higher prime

        :param new_capacity: The capacity to ensure as a prime number

        :return: The input capacity if it's prime or the next higher prime
        """
        if not self._is_prime(new_capacity):
            new_capacity = self._next_prime(new_capacity)

        return new_capacity

    def get_bucket_index(self, key: str) -> int:
        """
        Get the index of the bucket where the given key should be stored

        :param key: The key for which to calculate the bucket index

        :return: The calculated index of the bucket for the given key
        """
        # Calculate the hash code for the key using the hash function
        hash_code = self._hash_function(str(key))

        # Calculate the index using the modulo operation with the number of buckets
        index = hash_code % self._capacity

        return index

    def insert_hash_entry(self, index: int, hash_entry: object) -> None:
        """
        Insert a HashEntry object into the specified index of the hash table

        :param index: The index of the bucket where the hash entry should be inserted

        :param hash_entry: The hash entry object to be inserted

        :return: None
        """

        self._buckets[index] = hash_entry
        self._size += 1

    def update_hash_entry_value(self, index: int, key: str, value: object) -> None:
        """
        Update the value of a HashEntry object at the specified index or its probe location

        :param index: The index of the initial bucket

        :param key: The key associated with the HashEntry to update

        :param value: The new value to set for the HashEntry

        :return: None
        """
        # Get the bucket at the specified index
        bucket = self._buckets[index]

        # Check if the bucket key matches and is not a tombstone
        if bucket.key == key and bucket.is_tombstone is not True:
            bucket.value = value
        else:
            # Perform quadratic probing to find the next available index
            next_index = self.quad_probe(index, key)
            bucket = self._buckets[next_index]

            # Check if the bucket is None or a tombstone
            if bucket is None or bucket.is_tombstone is not False:
                # Create a new HashEntry and insert it at the next available index
                hash_entry = self.get_hash_entry(key, value)
                self.insert_hash_entry(next_index, hash_entry)
            else:
                # Update the value of the existing bucket
                bucket.value = value

    def quad_probe(self, index: int, key: str) -> int:
        """
        Performs a quadratic probing to find the next available index for the given key

        :param index: The initial index to start quadratic probing from

        :param key: The key for which to find the next available index

        :return: The next available index for the given key
        """
        probe_step = 1

        probing = True

        # Perform quadratic probing until an available index is found
        while probing:
            next_index = (index + probe_step ** 2) % self._buckets.length()
            bucket = self._buckets[next_index]

            if bucket is None:
                probing = False
                return next_index

            if bucket.key == key:
                probing = False
                return next_index
            else:
                probe_step += 1

    def process_key_and_value(self, key: str, value: object) -> None:
        """
        Process a key-value pair for insertion or updating in the hash table

        :param key: The key to be processed

        :param value: The value associated with the key

        :return: None
        """
        # Calculate the bucket index for the key
        bucket_index = self.get_bucket_index(key)

        # Get the bucket at the calculated index
        bucket = self._buckets[bucket_index]

        # Create a new HashEntry with the given key and value
        hash_entry = self.get_hash_entry(key, value)

        # Check if bucket is None or a tombstone
        if bucket is None or bucket.is_tombstone is not False:
            self.insert_hash_entry(bucket_index, hash_entry)
        else:
            self.update_hash_entry_value(bucket_index, key, value)

    def update_tombstone(self, index: int) -> None:
        """
        Update a bucket at the specified index to mark it as a tombstone

        :param index: The index of the bucket to mark as a tombstone

        :return: None
        """
        bucket = self._buckets[index]
        bucket.is_tombstone = True
        self._size -= 1

    def rehash(self, original_table, count=0) -> None:
        """
        Rehash the original table into the current hash table

        :param original_table: The original hash table to rehash from

        :param count: Counter to track the progress of rehashing

        :return: None
        """
        # Create a temporary DynamicArray to hold rehashed buckets
        temp_table = DynamicArray()

        # Iterate through each bucket in the original table
        while count < original_table.length():
            bucket = original_table[count]

            if bucket is not None and bucket.is_tombstone is not True:
                # Append the bucket to the temporary table and process the key-value pair
                temp_table.append(bucket)
                self.process_key_and_value(bucket.key, bucket.value)
                load_factor = self.table_load()

                if load_factor > 0.5:
                    # Double the capacity and rehash if needed
                    new_capacity = self._capacity
                    new_capacity *= 2
                    new_capacity = self.ensure_capacity_is_prime(new_capacity)
                    self._capacity = new_capacity

                    # Backup the current table and clear it
                    temp_table = self._buckets
                    self.clear()

                    # Rehash the non-tombstone buckets from the backup table
                    for i in range(0, temp_table.length()):
                        temp_bucket = temp_table[i]

                        if temp_bucket is not None and temp_bucket.is_tombstone is not True:
                            self.process_key_and_value(temp_bucket.key, temp_bucket.value)

            # Increment the counter to move to the next bucket
            count += 1

    # ------------------------------------------------------------------ #

    def put(self, key: str, value: object) -> None:
        """
        Insert or update a key-value pair in the hash table

        :param key: The key to be inserted or updated

        :param value: The value associated with the key

        :return: None
        """
        load_factor = self.table_load()

        # Check if load factor exceeds or is equal to 0.5, and resize if needed
        if load_factor >= 0.5:
            new_capacity = self._capacity * 2
            self.resize_table(new_capacity)

        bucket_index = self.get_bucket_index(key)

        # Check if the calculated index exceeds the current capacity, and resize if needed
        if bucket_index > self._capacity - 1:
            new_capacity = self._capacity * 2
            self.resize_table(new_capacity)

        # Process the key-value pair by inserting or updating
        self.process_key_and_value(key, value)

    def table_load(self) -> float:
        """
        Calculates the load factor of the hash table

        :return: The load factor as a floating point value
        """
        num_buckets = self.get_capacity()
        num_elements = self.get_size()
        load_factor = num_elements / num_buckets

        return load_factor

    def empty_buckets(self) -> int:
        """
        Counts the number of empty buckets in the hash table

        :return: The number of empty buckets
        """
        num_empty_buckets = 0

        # Iterate through each bucket in the hash table
        for i in range(0, self.get_capacity()):
            if self._buckets[i] is None:
                num_empty_buckets += 1

        return num_empty_buckets

    def resize_table(self, new_capacity: int) -> None:
        """
        Resize the hash table to the specified new capacity

        :param new_capacity: The new capacity to resize the hash table to

        :return: None
        """
        if new_capacity >= self._size:
            new_capacity = self.ensure_capacity_is_prime(new_capacity)
            self._capacity = new_capacity

            # Backup original buckets
            original_table = self._buckets

            self.clear()

            # Rehash the original buckets into the new hash table
            self.rehash(original_table)

    def get(self, key: str) -> object:
        """
        Retrieve the value associated with the given key from the hash table

        :param key: The key for which to retrieve the value

        :return: The value associated with the key, or None if the key is not found
        """
        if self._buckets.length() > 0:
            bucket_index = self.get_bucket_index(key)
            bucket = self._buckets[bucket_index]

            # Key not found
            if bucket is None:
                return None

            # Check if the bucket key matches and is not a tombstone
            if bucket.key == key and bucket.is_tombstone is not True:
                return bucket.value
            else:
                # Perform quadratic probing to find the next available index
                next_index = self.quad_probe(bucket_index, key)
                bucket = self._buckets[next_index]

                # Key not found
                if bucket is None:
                    return None

                if bucket.key == key and bucket.is_tombstone is not True:
                    return bucket.value

        return None

    def contains_key(self, key: str) -> bool:
        """
        Check if the hash table contains a key

        :param key: The key to check for in the hash table

        :return: True if the key exists, False otherwise
        """
        if self._buckets.length() > 0:
            bucket_index = self.get_bucket_index(key)
            bucket = self._buckets[bucket_index]

            if bucket is None:
                return False

            # Check if bucket key matches and is not tombstone
            if bucket.key == key and bucket.is_tombstone is not True:
                return True
            else:
                # Perform quadratic probing to find the next available index
                next_index = self.quad_probe(bucket_index, key)
                bucket = self._buckets[next_index]

                if bucket is None:
                    return False

                if bucket.key == key and bucket.is_tombstone is not True:
                    return True

        return False

    def remove(self, key: str) -> None:
        """
        Removes a key-value pair from the hash table based on the given key

        :param key: The key for the key-value pair to remove

        :return: None
        """

        if self._buckets.length() > 0:
            bucket_index = self.get_bucket_index(key)
            bucket = self._buckets[bucket_index]

            if bucket is not None:
                if bucket.key == key and bucket.is_tombstone is not True:
                    # Mark bucket as tombstone
                    self.update_tombstone(bucket_index)
                else:
                    # Perform quadratic probing to find next available index
                    next_index = self.quad_probe(bucket_index, key)
                    bucket = self._buckets[next_index]

                    if bucket is not None:
                        if bucket.key == key and bucket.is_tombstone is not True:
                            # Mark bucket as tombstone
                            self.update_tombstone(next_index)

    def clear(self) -> None:
        """
        Clear the contents of the hash table

        :return: None
        """
        self._buckets = DynamicArray()

        # Populate the new DynamicArray with None to represent empty buckets
        for _ in range(self._capacity):
            self._buckets.append(None)

        self._size = 0

    def get_keys_and_values(self) -> DynamicArray:
        """
        Retrieve keys and their corresponding values from the hash table

        :return: A DynamicArray of tuples containing keys and values
        """
        # Create a new DynamicArray to store key-value tuples
        da = DynamicArray()

        # Iterate through each bucket in the hash table
        for i in range(0, self._buckets.length()):
            bucket = self._buckets[i]

            if bucket is not None:
                if bucket.is_tombstone is not True:
                    # Append the kay-value tuple to the DynamicArray
                    da.append((bucket.key, bucket.value))

        return da


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
    keys = [i for i in range(25, 1000, 13)]
    for key in keys:
        m.put(str(key), key * 42)
    print(m.get_size(), m.get_capacity())

    for capacity in range(111, 1000, 117):
        m.resize_table(capacity)

        if m.table_load() > 0.5:
            print(
                f"Check that the load factor is acceptable after the call to resize_table().\n"
                f"Your load factor is {round(m.table_load(), 2)} and should be less than or equal to 0.5"
            )

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
    m = HashMap(11, hash_function_1)
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

    print("\nPDF - get_keys_and_values example 1")
    print("------------------------")
    m = HashMap(11, hash_function_2)
    for i in range(1, 6):
        m.put(str(i), str(i * 10))
    print(m.get_keys_and_values())

    m.resize_table(2)
    print(m.get_keys_and_values())

    m.put("20", "200")
    m.remove("1")
    m.resize_table(12)
    print(m.get_keys_and_values())

    print("\nPDF - __iter__(), __next__() example 1")
    print("---------------------")
    m = HashMap(10, hash_function_1)
    for i in range(5):
        m.put(str(i), str(i * 10))
    print(m)
    for item in m:
        print("K:", item.key, "V:", item.value)

    print("\nPDF - __iter__(), __next__() example 2")
    print("---------------------")
    m = HashMap(10, hash_function_2)
    for i in range(5):
        m.put(str(i), str(i * 24))
    m.remove("0")
    m.remove("4")
    print(m)
    for item in m:
        print("K:", item.key, "V:", item.value)
