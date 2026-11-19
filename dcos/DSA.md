# DSA

## 01. Two Sum

| Input | Expected output |
| --- | --- |
| `nums = [2, 7, 11, 19]`, `target = 9` | `[0, 1]` |

The output contains **indices**: `nums[0] + nums[1] = 2 + 7 = 9`.

```python
def two_sum(nums, target):
    seen = {}  # needed number -> index

    for i, value in enumerate(nums):
        if value in seen:
            return [seen[value], i]

        delta = target - value
        seen[delta] = i

    return []
```

**Recall clue:** Store what I need; check whether the current number supplies it.

## 02. Contains Duplicate: track what you have seen

| Input | Expected output |
| --- | --- |
| `nums = [1, 2, 3, 1]` | `True` |
| `nums = [1, 2, 3]` | `False` |

Return `True` if any value appears more than once.

```python
def contains_duplicate(nums):
    seen = set()
    for value in nums:
        if value in seen:
            return True
        seen.add(value)
    return False


print(contains_duplicate([1, 2, 3, 1]))
# True
```

**Recall clue:** Already seen? Return True. Otherwise, remember it.

## 03. Frequency counting: build a histogram

| Input | Expected output |
| --- | --- |
| `items = ["A", "B", "A", "C", "B", "A"]` | `{'A': 3, 'B': 2, 'C': 1}` |

Each dictionary value is the number of times its key appears.

```python
def frequencies(items):
    counts = {}  # value: count
    for value in items:
        if value in counts:
            counts[value] = counts[value] + 1
        else:
            counts[value] = 1
    return counts


print(frequencies(["A", "B", "A", "C", "B", "A"]))
# {'A': 3, 'B': 2, 'C': 1}
```

## 03a. LC #49 — Group Anagrams

| Input | Expected output |
| --- | --- |
| `strs = ["eat", "tea", "tan", "ate", "nat", "bat"]` | `[["eat", "tea", "ate"], ["tan", "nat"], ["bat"]]` |

Words with the same character counts belong in the same group. Group order and word order within a group do not matter for this problem.

```python
from collections import defaultdict


def lc49(strs):
    dct = defaultdict(list)
    result = []
    for str in strs:
        key = "".join(sorted(str))
        if key in dct:
            dct[key].append(str)
        else:
            dct[key] = [str]
    for value in dct.values():
        result.append(value)
    return result
```

## 04. Top K Frequent Elements: keep the best k

| Input | Expected output |
| --- | --- |
| `nums = [1, 1, 1, 2, 2, 3]`, `k = 2` | `[2, 1]` |

`1` appears three times and `2` appears twice, making them the two most frequent values. `[1, 2]` is also valid; output order does not matter.

```python
import heapq


def top_k_frequent(nums, k):
    counts = {}
    for val in nums:
        counts[val] = counts.get(val, 0) + 1

    heap = []
    for value, count in counts.items():
        heapq.heappush(heap, (count, value))
        if len(heap) > k:
            heapq.heappop(heap)

    return [value for count, value in heap]


print(top_k_frequent([1, 1, 1, 2, 2, 3], 2))
# [2, 1]
```

### 04b. Merge two sorted lists of numbers using a heap

Each input is an ordinary Python list sorted in ascending order. Keep only the next unused value from each list in the heap. Pop the smallest, then add the next value from that same list.

```python
import heapq


def merge_sorted_lists(l1, l2):
    lists = [l1, l2]
    heap = []
    for source, values in enumerate(lists):
        if values:
            heapq.heappush(heap, (values[0], source, 0))

    result = []
    while heap:
        value, source, index = heapq.heappop(heap)
        result.append(value)

        index += 1
        if index < len(lists[source]):
            heapq.heappush(heap, (lists[source][index], source, index))

    return result


l1 = [1, 5, 10, 27, 30]
l2 = [3, 4, 6]
print(merge_sorted_lists(l1, l2))
# Expected: [1, 3, 4, 5, 6, 10, 27, 30]

print(merge_sorted_lists([1, 2, 2], [2, 3]))
# Expected: [1, 2, 2, 2, 3]

print(merge_sorted_lists([], [3, 4]))
# Expected: [3, 4]
```

**Heap entry:** `(value, source, index)` stores the number, which input list it belongs to (`0` or `1`), and its position in that list. The value comes first, so the smallest number is popped first.

**Complexity:** O(m + n) time. The heap holds at most two entries: O(1) extra space excluding the O(m + n) output list.

## 05. Anagram detection

These examples apply to **both implementations below**.

| Input | Expected output |
| --- | --- |
| `s = "anagram"`, `t = "nagaram"` | `True` |
| `s = "rat"`, `t = "car"` | `False` |

Anagrams contain the same characters with the same counts, possibly in a different order.

### Sorting approach: compare sorted characters

```python
def is_anagram(s, t):
    if len(s) != len(t):
        return False

    sorted_s = "".join(sorted(s))
    sorted_t = "".join(sorted(t))
    for i in range(len(s)):
        if sorted_s[i] != sorted_t[i]:
            return False

    return True
```

**Time:** O(n log n). **Space:** O(n).

### Counting approach: compare character counts

```python
def is_anagram_o_n(s, t):
    if len(s) != len(t):
        return False

    counts = {}
    for char in s:
        counts[char] = counts.get(char, 0) + 1

    for char in t:
        if counts.get(char, 0) == 0:
            return False
        counts[char] -= 1

    return True
```

**Time:** O(n). Two separate passes: O(n) + O(n) = O(n).

## 05a. LC #128 — Longest Consecutive Sequence

| Input | Expected output from your practice function |
| --- | --- |
| `nums = [100, 4, 200, 1, 3, 2]` | `(4, [1, 2, 3, 4])` |

The longest consecutive sequence is `[1, 2, 3, 4]`, with length `4`. The numbers do not need to be adjacent in the input. LC #128 itself expects only `4`.

```python
def lc_128(nums):
    seen = set()
    max_len = 0
    result = []
    poss_seq = []

    for num in nums:
        seen.add(num)

    for num in seen:
        if num - 1 not in seen:
            curr_num = num
            poss_seq = []

            while curr_num in seen:
                poss_seq.append(curr_num)
                curr_num += 1

            if max_len < len(poss_seq):
                max_len = len(poss_seq)
                result = poss_seq

    return max_len, result


nums = [100, 4, 200, 1, 3, 2]
print(lc_128(nums))
# (4, [1, 2, 3, 4])
```

**For LeetCode:** use `return max_len` because LC #128 expects only the length. The version above returns both the length and longest sequence for practice.

**Time:** O(n) expected. Iterating over `seen` prevents duplicate starting numbers from rescanning a sequence. **Space:** O(n).

## 06. Longest unique substring: a simple baseline

| Input | Expected output | A longest valid substring |
| --- | --- | --- |
| `s = "abcabcbb"` | `3` | `"abc"` |
| `s = "bbbbb"` | `1` | `"b"` |
| `s = "dvdf"` | `3` | `"vdf"` |
| `s = ""` | `0` | `""` |

Return the length of the longest contiguous substring with no repeated characters. Characters must be adjacent; you cannot skip positions.

```python
def longest_unique_bruteforce(s):
    best = 0
    for start in range(len(s)):
        seen = set()
        for end in range(start, len(s)):
            if s[end] in seen:
                break
            seen.add(s[end])
            best = max(best, end - start + 1)
    return best
```

**Critical note:** Update `best` inside the inner loop, immediately after `seen.add()`, so the duplicate that triggers `break` is never counted.

**Time:** O(n²) worst case. **Space:** O(n) worst case.

### Optimized version: sliding window

Keep the current unique substring. When a duplicate arrives, remove characters from the left until the old copy is gone, then add the new character.

| Input | Expected output | A longest valid substring |
| --- | --- | --- |
| `s = "dvdf"` | `3` | `"vdf"` |
| `s = "abba"` | `2` | `"ab"` or `"ba"` |
| `s = ""` | `0` | `""` |

```python
def longest_unique(s):
    seen = set()
    left = 0
    best = 0

    for right in range(len(s)):
        while s[right] in seen:
            seen.remove(s[left])
            left += 1

        seen.add(s[right])
        best = max(best, right - left + 1)

    return best
```

**Critical note:** Use `while` because removing the duplicate may require removing several characters from the left.

**Time:** O(n) expected: each character enters the window once and leaves at most once. **Space:** O(n) worst case.

**Recall clue:** Duplicate? Shrink left. Then add right and update best.

## 07. String compression: read runs, write compactly

Read one consecutive group, then write its shorter form. For `"aabbbc"`: read `"aa"` and write `"a2"`; read `"bbb"` and write `"b3"`; read `"c"` and write `"c"`.

| Input | Returned length `k` | Valid output `chars[:k]` |
| --- | --- | --- |
| `chars = list("aabbbc")` | `5` | `['a', '2', 'b', '3', 'c']` |
| `chars = list("aabaa")` | `5` | `['a', '2', 'b', 'a', '2']` |
| `chars = list("aabbbcccccccccc")` | `7` | `['a', '2', 'b', '3', 'c', '1', '0']` |

Modify the original list and return the number of positions used. Anything after the first `k` positions is irrelevant.

- `read`: where you are reading the original characters.
- `write`: where you will write the next compressed character.

```python
def compress(chars):
    read = 0
    write = 0

    while read < len(chars):
        char = chars[read]
        count = 0

        # Read one whole group.
        while read < len(chars) and chars[read] == char:
            count += 1
            read += 1

        # Write its character.
        chars[write] = char
        write += 1

        # Write its count, if repeated.
        if count > 1:
            for digit in str(count):
                chars[write] = digit
                write += 1

    return write


chars = list("aabbbc")
k = compress(chars)
print(k)          # 5
print(chars[:k])   # ['a', '2', 'b', '3', 'c']
```

**Critical notes:** Reset `count` for each group. Omit counts of 1. Write a multi-digit count one digit at a time: `10` becomes `'1'`, `'0'`.

**Time:** O(n). **Extra space:** O(log n) temporarily for `str(count)`; no separate compressed list is built. The example's `chars[:k]` slice is only for displaying the result.

**Recall clue:** Read one group, then write its shorter form.

## 08. Reverse words: normalize whitespace

Reverse the order of the words. Keep each word's letters in their original order, remove leading/trailing whitespace, and place one space between words.

| Input | Expected output |
| --- | --- |
| `s = "  the sky   is blue  "` | `"blue is sky the"` |
| `s = "hello\tworld\nagain"` | `"again world hello"` |
| `s = "   "` | `""` |

```python
def reverse_words(s):
    words = s.split()
    words.reverse()
    return " ".join(words)


print(reverse_words("  the sky   is blue  "))
# blue is sky the
```

**Critical note:** `split()` handles whitespace runs and drops empty pieces. `split(" ")` uses a literal space separator and can produce empty strings.

**Time:** O(n). **Extra space:** O(n).

**Recall clue:** Split words, reverse their order, join with one space.

Related problem: [LC #151 — Reverse Words in a String](https://leetcode.com/problems/reverse-words-in-a-string/). It includes a follow-up about modifying mutable input with O(1) extra space.

### 08a. Reverse words: build words manually

Return the same result as exercise 08, using a manual scan.

- Build the words manually without `split()` or regular expressions.
- Any whitespace separates words, including tabs and newlines. Remove leading/trailing whitespace and use one ordinary space between output words.
- Reverse slicing (`[::-1]`) and `join()` are allowed for the final result.

| Input | Expected output |
| --- | --- |
| `s = "  hello   world "` | `"world hello"` |
| `s = "hello world"` | `"world hello"` |
| `s = "  the sky   is blue  "` | `"blue is sky the"` |
| `s = "hello\tworld\nagain"` | `"again world hello"` |
| `s = "   "` | `""` |

```python
def reverse_8a(s):
    lst = list(s)
    lstWords = []
    word = []
    for char in lst:
        if char.isspace():
            if len(word) > 0:
                word = "".join(word)
                lstWords.append(word)
                word = []
        else:
            word.append(char)

    if len(word) > 0:
        word = "".join(word)
        lstWords.append(word)

    return " ".join(lstWords[::-1])
```

**Critical note:** After the loop, save any remaining word. If the input has no trailing whitespace, that word has not yet been added to `lstWords`.

**Complexity:** O(n) time and O(n) extra space, where n is the length of the input string.

**Practice focus:** Finding word boundaries and handling whitespace yourself. Aim for O(n) time; O(n) output space is allowed.

### 08b. Reverse word order in place

```python
def reverse_8b(chars):
    def reverse(left, right):
        while left < right:
            chars[left], chars[right] = chars[right], chars[left]
            left += 1
            right -= 1

    # Step 1: reverse the entire character list
    reverse(0, len(chars) - 1)

    # Step 2: reverse each word
    start = 0
    for end in range(len(chars) + 1):
        if end == len(chars) or chars[end] == " ":
            reverse(start, end - 1)
            start = end + 1
```

### 08c. Reverse each word, preserve whitespace

```python
def reverse_8c(s):
    chars = list(s)

    def reverse(left, right):
        while left < right:
            chars[left], chars[right] = chars[right], chars[left]
            left += 1
            right -= 1

    # Reverse each word only
    start = 0
    for end in range(len(chars) + 1):
        if end == len(chars) or chars[end].isspace():
            reverse(start, end - 1)
            start = end + 1

    return "".join(chars)
```

## 09. Linked lists

### 09a. Reverse a linked list

```python
class Node:
    def __init__(self, val, next=None):
        self.val = val
        self.next = next


def build_linked_list(values):
    dummy = Node(0)
    curr = dummy
    for val in values:
        curr.next = Node(val)
        curr = curr.next
    return dummy.next


def reverse_ll(head):
    prev = None
    next_node = None
    curr = head
    while curr:
        next_node = curr.next
        curr.next = prev
        prev = curr
        curr = next_node
    return prev


head = build_linked_list([1, 2, 3])
head = reverse_ll(head)
# Expected node values: [3, 2, 1]
```

**Reversal complexity:** O(n) time, O(1) extra space.

### 09b. LC #21 — Merge two sorted linked lists

Uses `Node` and `build_linked_list` from 09a.

```python
def lc21(l1, l2):
    dummy = Node(0)
    tail = dummy
    while l1 and l2:
        if l1.val < l2.val:
            tail.next = l1
            l1 = l1.next
        else:
            tail.next = l2
            l2 = l2.next
        tail = tail.next
    tail.next = l1 if l1 else l2
    return dummy.next


l1_vals = [1, 5, 10, 27, 30]
l2_vals = [3, 4, 6]
l1 = build_linked_list(l1_vals)
l2 = build_linked_list(l2_vals)
merged = lc21(l1, l2)
# Expected node values: [1, 3, 4, 5, 6, 10, 27, 30]
```

**Merge complexity:** O(m + n) time, O(1) extra space; reuses the existing nodes.

### 09c. LC #25 — Reverse Nodes in k-Group

Reverse every full group of `k` nodes. Leave a final group smaller than `k` unchanged. Reuses `Node`, `build_linked_list`, and `reverse_ll` from 09a; `k >= 1`.

```python
def reverse_k_group(head, k):
    dummy = Node(0, head)
    before = dummy

    while True:
        # Find the last node of a full group
        end = before
        for _ in range(k):
            end = end.next
            if end is None:
                return dummy.next

        start = before.next
        after = end.next

        # Detach this group
        end.next = None

        # Reverse using your existing function
        before.next = reverse_ll(start)

        # Reconnect and move to the next group
        start.next = after
        before = start


head = build_linked_list([1, 2, 3, 4, 5])
head = reverse_k_group(head, 2)
# Expected node values: [2, 1, 4, 3, 5]
```

**Complexity:** O(n) time, O(1) extra space.

### 09d. Find the middle: fast and slow pointers

Uses `Node` and `build_linked_list` from 09a. Slow moves one node; fast moves two. When fast reaches the end, slow is at the middle.

```python
def find_middle(head):
    slow = head
    fast = head

    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next

    return slow


head = build_linked_list([1, 2, 3, 4, 5])
print(find_middle(head).val)  # Expected: 3

head = build_linked_list([1, 2, 3, 4])
print(find_middle(head).val)  # Expected: 3 (second middle)

print(find_middle(None))     # Expected: None
```

**Critical note:** Returns the middle node. For even-length lists, returns the second middle. Assumes the list has no cycle.

**Complexity:** O(n) time, O(1) extra space.

### 09e. Detect a cycle: fast catches slow

Uses the same pointer movement as 09d. If there is a cycle, fast eventually catches slow at the same node.

```python
def has_cycle(head):
    slow = head
    fast = head

    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:
            return True

    return False


head = build_linked_list([1, 2, 3])
print(has_cycle(head))       # Expected: False

head = build_linked_list([1, 1])
print(has_cycle(head))       # Expected: False (distinct nodes)

head = build_linked_list([1, 2, 3])
head.next.next.next = head.next  # Node 3 links back to node 2
print(has_cycle(head))       # Expected: True

print(has_cycle(None))       # Expected: False
```

**Critical note:** Compare node identity (`is`), not node values. Check after moving, because both pointers start at `head`.

**Complexity:** O(n) time, O(1) extra space.

## 10. Stacks and queues

### 10a. Valid Parentheses

Every closing bracket must match the most recent unmatched opening bracket.

```python
def valid_parentheses(s):
    pairs = {")": "(", "]": "[", "}": "{"}
    stack = []

    for char in s:
        if char in "([{":
            stack.append(char)
        elif not stack or stack.pop() != pairs.get(char):
            return False

    return not stack


print(valid_parentheses("([{}])"))  # Expected: True
print(valid_parentheses("()[]{}"))  # Expected: True
print(valid_parentheses("([)]"))    # Expected: False
print(valid_parentheses("(("))      # Expected: False
print(valid_parentheses(")"))       # Expected: False
```

**Critical note:** The final `not stack` rejects opening brackets that never got closed.

**Complexity:** O(n) time and O(n) space.

### 10b. Min Stack implementation

Keep the values in `stack` and track new or repeated minima in `mins`.

```python
class MinStack:
    def __init__(self):
        self.stack = []
        self.mins = []

    def push(self, value):
        self.stack.append(value)
        if not self.mins or value <= self.mins[-1]:
            self.mins.append(value)

    def pop(self):
        value = self.stack.pop()
        if value == self.mins[-1]:
            self.mins.pop()
        return value

    def top(self):
        return self.stack[-1]

    def get_min(self):
        return self.mins[-1]


stack = MinStack()
stack.push(3)
stack.push(1)
stack.push(1)
print(stack.get_min())  # Expected: 1
print(stack.pop())      # Expected: 1
print(stack.get_min())  # Expected: 1 (another 1 remains)
print(stack.pop())      # Expected: 1
print(stack.get_min())  # Expected: 3
print(stack.top())      # Expected: 3
```

**Critical note:** Use `<=` when recording minima so duplicate minimum values are handled correctly. `pop`, `top`, and `get_min` require a nonempty stack.

**Complexity:** O(1) amortized per operation; O(n) space.

### 10c. Queue implementation using two stacks

A queue returns the oldest value first (FIFO). Reuse `append()` and `pop()` on two stacks: `incoming` receives new values; `outgoing` serves the oldest ones. Moving values between them reverses their order.

```python
class Queue:
    def __init__(self):
        self.incoming = []
        self.outgoing = []

    def enqueue(self, value):
        self.incoming.append(value)

    def _shift(self):
        if not self.outgoing:
            while self.incoming:
                self.outgoing.append(self.incoming.pop())

    def dequeue(self):
        self._shift()
        return self.outgoing.pop()

    def peek(self):
        self._shift()
        return self.outgoing[-1]

    def is_empty(self):
        return not self.incoming and not self.outgoing


queue = Queue()
queue.enqueue(10)
queue.enqueue(20)
print(queue.peek())      # Expected: 10
print(queue.dequeue())   # Expected: 10
queue.enqueue(30)
print(queue.dequeue())   # Expected: 20
print(queue.dequeue())   # Expected: 30
print(queue.is_empty())  # Expected: True
```

**Critical note:** Transfer only when `outgoing` is empty; this preserves FIFO order when new values arrive. `dequeue` and `peek` require a nonempty queue.

**Complexity:** O(1) amortized per operation; a transfer can take O(n) in one call. O(n) space.

## 11. SlidingWindow

**Pattern:** Grow right → adjust left → record the answer.

### 11a. LC #643 — Maximum Average Subarray I: fixed-size window

Find the highest average among all groups of exactly `k` consecutive numbers. Assume `1 <= k <= len(nums)`.

**Goal:** Fixed size. Adjust left when size > `k`; record the answer when size == `k`.

Since every complete window has the same size, the largest sum also gives the largest average.

```python
def max_average(nums, k):
    left = 0
    window_sum = 0
    best_sum = float("-inf")

    for right in range(len(nums)):
        # GROW RIGHT: include the new number
        window_sum += nums[right]

        # ADJUST LEFT: remove the oldest number if size > k
        if right - left + 1 > k:
            window_sum -= nums[left]
            left += 1

        # RECORD ANSWER: only when size == k
        if right - left + 1 == k:
            best_sum = max(best_sum, window_sum)

    return best_sum / k


nums = [2, 1, 5, 1, 3, 2]
k = 3
print(max_average(nums, k))  # Expected: 3.0
```

**Critical note:** `best_sum` starts at negative infinity so the code also works when every window's sum is negative.

**Complexity:** O(n) time, O(1) extra space.

### 11b. LC #567 — Permutation in String: fixed-size window

Return `True` if any rearrangement of `s1` occurs as a continuous substring of `s2`. Inputs are nonempty strings of lowercase English letters.

Reuse 11a's fixed-window structure, tracking character counts instead of a running sum. The window size is `k = len(s1)`.

```python
def contains_permutation(s1, s2):
    k = len(s1)
    if k > len(s2):
        return False

    need = {}
    for char in s1:
        need[char] = need.get(char, 0) + 1

    window = {}
    left = 0

    for right in range(len(s2)):
        # GROW RIGHT: include the new character
        char = s2[right]
        window[char] = window.get(char, 0) + 1

        # ADJUST LEFT: remove the oldest character if size > k
        if right - left + 1 > k:
            char = s2[left]
            window[char] -= 1
            if window[char] == 0:
                del window[char]
            left += 1

        # CHECK ANSWER: size == k and character counts match
        if right - left + 1 == k and window == need:
            return True

    return False


print(contains_permutation("ab", "eidbaooo"))   # Expected: True, "ba"
print(contains_permutation("ab", "eidboaoo"))   # Expected: False
print(contains_permutation("aab", "eidbaaoo"))  # Expected: True, "baa"
```

**Critical note:** Delete entries whose count becomes zero. An extra entry such as `"e": 0` would otherwise make the dictionaries unequal.

**Complexity:** O(len(s1) + len(s2)) time and O(1) auxiliary space for the fixed lowercase English alphabet: each dictionary holds at most 26 keys.

### 11c. LC #1004 — Max Consecutive Ones III: longest valid window

Given a binary array, find the longest consecutive section that could become all ones by flipping at most `k` zeros, where `k >= 0`.

**Intuition:** Each zero costs one flip. A window is valid while its zero count is <= `k`; count zeros without changing the array. Here `k` is the flip allowance, not the window size.

```python
def longest_ones(nums, k):
    left = 0
    zeros = 0
    best = 0

    for right in range(len(nums)):
        # GROW RIGHT: count the incoming zero, if any
        if nums[right] == 0:
            zeros += 1

        # ADJUST LEFT: shrink WHILE we need too many flips
        while zeros > k:
            if nums[left] == 0:
                zeros -= 1
            left += 1

        # RECORD ANSWER: the window is now valid
        best = max(best, right - left + 1)

    return best


nums = [1, 0, 1, 1, 0]
print(longest_ones(nums, 1))  # Expected: 4
# Window [1, 0, 1, 1] could become [1, 1, 1, 1].

print(longest_ones(nums, 0))  # Expected: 2
```

**Recall:** Grow → shrink while `zeros > k` → record longest length. Use `while` because removing one element may not make the window valid.

**Complexity:** O(n) time, O(1) space.

### 11d. LC #424 — Longest Repeating Character Replacement

Find the longest substring that can become one repeated letter by changing at most `k` characters. Inputs contain uppercase English letters, and `k >= 0`.

**Intuition:** Reuse 11c's longest-valid-window pattern. Keep the most frequent letter in the window and change everything else:

`changes needed = window length - highest character count`

```python
def character_replacement(s, k):
    left = 0
    counts = {}
    best = 0

    for right in range(len(s)):
        # GROW RIGHT: count the incoming character
        char = s[right]
        counts[char] = counts.get(char, 0) + 1

        # ADJUST LEFT: shrink while too many changes are needed
        while right - left + 1 - max(counts.values()) > k:
            counts[s[left]] -= 1
            left += 1

        # RECORD ANSWER: the window is now valid
        best = max(best, right - left + 1)

    return best


print(character_replacement("AABABBA", 1))  # Expected: 4
# "AABA" becomes "AAAA" by changing one B.

print(character_replacement("ABAB", 2))     # Expected: 4
# Change both B characters to A.
```

**Recall:** Grow → shrink while changes exceed `k` → record longest length.

**Complexity:** For uppercase English letters, `max(counts.values())` checks at most 26 counts. O(26n) = O(n) time and O(1) space.

## 12. Trees

### 12a. Binary-tree node: build from your linked-list node

Your linked-list node stores a value and one `next` reference. A binary-tree node stores a value and two child references: `left` and `right`. Each child can be another node or `None`.

```python
class TreeNode:
    def __init__(self, val, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


# Build a tree with root 1, left child 2, and right child 3.
root = TreeNode(1)
root.left = TreeNode(2)
root.right = TreeNode(3)

print(root.val)         # Expected: 1
print(root.left.val)    # Expected: 2
print(root.right.val)   # Expected: 3
print(root.left.left)   # Expected: None
```

| Input / expression | Expected output |
| --- | --- |
| The tree built above; `root.val` | `1` |
| `root.left.val` | `2` |
| `root.right.val` | `3` |
| `root.left.left` | `None` |

**Critical terms:** The root is the starting node, here node 1. A leaf has no children; nodes 2 and 3 are leaves. Each node, together with all its descendants, forms a subtree.

**Recall:** Linked list: value + next. Binary tree: value + left + right.

### 12b. Iterative DFS (preorder): visit nodes using a stack

Reuse `append()` and `pop()` from section 10. Visit node → left subtree → right subtree. Uses `TreeNode` from 12a.

```python
def dfs(root):
    if root is None:
        return []

    stack = [root]
    result = []

    while stack:
        node = stack.pop()
        result.append(node.val)

        # Push right first, so left gets popped first.
        if node.right:
            stack.append(node.right)
        if node.left:
            stack.append(node.left)

    return result


root = TreeNode(1)
root.left = TreeNode(2)
root.right = TreeNode(3)
root.left.left = TreeNode(4)

print(dfs(root))  # Expected: [1, 2, 4, 3]
print(dfs(None))  # Expected: []
```

**Recall:** Pop → record → push right → push left.

**Complexity:** O(n) time and O(n) space including the returned list.

### 12c. Iterative BFS (level order): visit nodes using a queue

Reuse 12b's traversal structure with a FIFO queue. Visit nodes one level at a time, from left to right. Uses `TreeNode` from 12a and returns a flat list of node values.

```python
from collections import deque


def bfs(root):
    if root is None:
        return []

    queue = deque([root])
    result = []

    while queue:
        node = queue.popleft()
        result.append(node.val)

        if node.left:
            queue.append(node.left)
        if node.right:
            queue.append(node.right)

    return result


root = TreeNode(1)
root.left = TreeNode(2)
root.right = TreeNode(3)
root.left.left = TreeNode(4)

print(bfs(root))  # Expected: [1, 2, 3, 4]
print(bfs(None))  # Expected: []
```

**Critical note:** `deque([root])` starts the queue with just the root node. `popleft()` removes the oldest item.

**Recall:** Dequeue → record → enqueue left → enqueue right.

**Complexity:** O(n) time and O(n) space including the returned list.

### 12d. Maximum depth of a binary tree: reuse DFS with depth

Return the number of nodes on the longest root-to-leaf path. An empty tree has depth 0. Reuse 12b's DFS, storing `(node, depth)` and keeping the largest depth seen. Uses `TreeNode` from 12a.

```python
def max_depth(root):
    if root is None:
        return 0

    stack = [(root, 1)]  # node, depth
    best = 0

    while stack:
        node, depth = stack.pop()
        best = max(best, depth)

        # Children are one level deeper.
        if node.right:
            stack.append((node.right, depth + 1))
        if node.left:
            stack.append((node.left, depth + 1))

    return best


# 1
# |---- 2 (left)
# |     |---- 4 (left)
# |---- 3 (right)
root = TreeNode(1)
root.left = TreeNode(2)
root.right = TreeNode(3)
root.left.left = TreeNode(4)

print(max_depth(root))  # Expected: 3
print(max_depth(None))  # Expected: 0
```

**Recall:** DFS + carry depth + keep the maximum.

**Complexity:** O(n) time and O(h) extra stack space, where h is tree height; O(n) space in the worst case.
