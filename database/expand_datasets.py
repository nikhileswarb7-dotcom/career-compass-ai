import os
import json
import csv

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_DIR = os.path.join(BASE_DIR, "database")
DATASETS_DIR = os.path.join(DB_DIR, "datasets")

# Subdirectories
HIRING_CSV_DIR = os.path.join(DB_DIR, "hiring_layer")
LEARNING_CSV_DIR = os.path.join(DB_DIR, "learning_layer")

# Master Skills Mapping (for Reference)
SKILLS_MAP = {
    1: "Go", 2: "Java", 3: "Python", 4: "Kafka", 5: "Redis", 6: "PostgreSQL",
    7: "Docker", 8: "Kubernetes", 9: "gRPC", 10: "Microservices", 11: "Spring Boot",
    12: "NodeJS", 13: "AWS", 14: "GCP", 15: "DynamoDB", 16: "MySQL",
    17: "ElasticSearch", 18: "Django", 19: "React", 20: "TypeScript", 21: "NextJS",
    22: "Kotlin", 23: "Android", 24: "SRE", 25: "System Design", 26: "Distributed Systems"
}
REVERSE_SKILLS_MAP = {v: k for k, v in SKILLS_MAP.items()}

# ==============================================================================
# PART 1: INTERVIEW QUESTIONS GENERATOR (350+ Questions)
# ==============================================================================
def generate_interview_questions():
    print("Generating 390+ SDE Interview Questions...")
    questions = []
    
    # 1. DSA (80 unique problems)
    dsa_list = [
        ("Two Sum", "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.", "Use a hash map to store seen numbers and their indices, checking if target - num exists.", "Time complexity is O(N) as we traverse the list once and lookup is O(1). Space complexity is O(N).", ["Arrays", "Hash Map"], "Very Common", "Easy"),
        ("Valid Parentheses", "Given a string containing just the characters '(', ')', '{', '}', '[' and ']', determine if the input string is valid.", "Use a stack to push opening brackets, and pop to match them when seeing closing brackets.", "Time Complexity: O(N), Space Complexity: O(N). Ensure the stack is empty at the end of traversal.", ["Stack"], "Very Common", "Easy"),
        ("Merge Two Sorted Lists", "Merge two sorted linked lists and return it as a new sorted list.", "Compare heads of both lists, link the smaller node, and advance its pointer.", "Time Complexity: O(N + M) where N and M are the lengths of the lists. Space Complexity: O(1).", ["Linked List"], "Very Common", "Easy"),
        ("Best Time to Buy and Sell Stock", "Find the maximum profit you can achieve by buying and selling a stock on different days.", "Track the minimum price seen so far and compute the profit on each day to find the max.", "Time Complexity: O(N) with a single pass. Space Complexity: O(1).", ["Arrays", "Dynamic Programming"], "Very Common", "Easy"),
        ("Valid Palindrome", "Determine if a string is a palindrome, considering only alphanumeric characters and ignoring cases.", "Use two pointers, one at the start and one at the end, moving towards the middle while comparing characters.", "Time Complexity: O(N), Space Complexity: O(1) as we modify in-place.", ["Two Pointers", "Strings"], "Common", "Easy"),
        ("Invert Binary Tree", "Invert a binary tree (swap left and right subtrees recursively).", "Use recursive DFS to swap left and right children of every node.", "Time Complexity: O(N) since we visit every node. Space Complexity: O(H) for recursion stack.", ["Trees", "Recursion"], "Very Common", "Easy"),
        ("Valid Anagram", "Given two strings s and t, return true if t is an anagram of s, and false otherwise.", "Count character frequencies using a hash map or an array of size 26 and compare them.", "Time Complexity: O(N), Space Complexity: O(1) if character set is fixed.", ["Strings", "Hash Map"], "Common", "Easy"),
        ("Binary Search", "Given a sorted array of integers nums and a target, search target in nums in O(log N) time.", "Use two pointers for low and high, find the mid point, and adjust bounds based on target comparison.", "Time Complexity: O(log N) as search space is halved. Space Complexity: O(1).", ["Binary Search"], "Very Common", "Easy"),
        ("Flood Fill", "Perform a flood fill on a 2D image array given a starting pixel, a new color, and matching adjacent colors.", "Use DFS or BFS starting from the given pixel to recursively color matching neighbor pixels.", "Time Complexity: O(N) where N is number of pixels. Space Complexity: O(N) for recursive call stack.", ["Graphs", "DFS", "BFS"], "Common", "Easy"),
        ("Lowest Common Ancestor of a BST", "Find the lowest common ancestor (LCA) node of two given nodes in a BST.", "Traverse the tree from the root. If both nodes are smaller, move left; if larger, move right; else this is LCA.", "Time Complexity: O(H) where H is tree height. Space Complexity: O(1) if iterative.", ["Trees", "BST"], "Common", "Easy"),
        ("Balanced Binary Tree", "Determine if a binary tree is height-balanced (heights of subtrees differ by at most 1).", "Compute node heights recursively. Return -1 if any subtree is unbalanced, avoiding redundant calculations.", "Time Complexity: O(N), Space Complexity: O(H) for recursion stack.", ["Trees", "DFS"], "Very Common", "Easy"),
        ("Linked List Cycle", "Determine if a linked list has a cycle in it.", "Use Floyd's tortoise and hare algorithm with slow and fast pointers. If they meet, there is a cycle.", "Time Complexity: O(N), Space Complexity: O(1) pointer checks.", ["Linked List", "Two Pointers"], "Very Common", "Easy"),
        ("Implement Queue using Stacks", "Implement a FIFO queue using only two stacks.", "Push elements to input stack. Pop from output stack; if empty, transfer all from input to output.", "Amortized O(1) for pop and peek. Space Complexity: O(N).", ["Stack", "Queue"], "Common", "Easy"),
        ("First Bad Version", "Find the first bad version in a series using an API check isBadVersion(version) with minimal API calls.", "Use binary search to find the boundary where versions change from good to bad.", "Time Complexity: O(log N), Space Complexity: O(1).", ["Binary Search"], "Common", "Easy"),
        ("Ransom Note", "Determine if a ransom note string can be constructed from characters in a magazine string.", "Count characters in the magazine and decrement them for characters in the ransom note.", "Time Complexity: O(N + M), Space Complexity: O(1) if using 26-size array.", ["Strings", "Hash Map"], "Common", "Easy"),
        ("Climbing Stairs", "Find the number of distinct ways to climb to the top of a staircase of N steps if you can take 1 or 2 steps.", "Use dynamic programming where ways(N) = ways(N-1) + ways(N-2).", "Time Complexity: O(N), Space Complexity: O(1) by keeping track of the last two values.", ["Dynamic Programming"], "Very Common", "Easy"),
        ("Longest Palindrome", "Given a string s, return the length of the longest palindrome that can be built with those letters.", "Count character frequencies. Add even frequencies to length, and add 1 at the end if there is any odd frequency.", "Time Complexity: O(N), Space Complexity: O(1) for character set storage.", ["Strings", "Hash Map"], "Common", "Easy"),
        ("Reverse Linked List", "Reverse a singly linked list in-place.", "Iterate through the list, changing curr.next to point to the prev node, maintaining a next pointer.", "Time Complexity: O(N), Space Complexity: O(1).", ["Linked List"], "Very Common", "Easy"),
        ("Majority Element", "Find the element that appears more than N/2 times in an array.", "Use Boyer-Moore Voting Algorithm to find the candidate with positive counter balance.", "Time Complexity: O(N), Space Complexity: O(1).", ["Arrays", "Sorting"], "Common", "Easy"),
        ("Add Binary", "Given two binary strings, return their sum as a binary string.", "Use two pointers starting from the ends of the strings, adding digits along with carry.", "Time Complexity: O(max(N, M)), Space Complexity: O(max(N, M)) for result.", ["Strings", "Math"], "Common", "Easy"),
        ("Diameter of Binary Tree", "Find the length of the longest path between any two nodes in a binary tree.", "Calculate height of left and right subtrees recursively. Diameter at a node is left_height + right_height.", "Time Complexity: O(N), Space Complexity: O(H) recursion stack.", ["Trees", "DFS"], "Common", "Easy"),
        ("Middle of the Linked List", "Return the middle node of a singly linked list.", "Use a slow pointer moving one step and a fast pointer moving two steps. Slow reaches middle when fast reaches end.", "Time Complexity: O(N), Space Complexity: O(1).", ["Linked List", "Two Pointers"], "Common", "Easy"),
        ("Maximum Depth of Binary Tree", "Find the maximum depth of a binary tree.", "Use recursive DFS where depth is 1 + max(depth(left), depth(right)).", "Time Complexity: O(N), Space Complexity: O(H).", ["Trees", "DFS"], "Very Common", "Easy"),
        ("Contains Duplicate", "Return true if any value appears at least twice in an array.", "Use a hash set to track seen elements. If element already in set, return true.", "Time Complexity: O(N), Space Complexity: O(N).", ["Arrays", "Hash Set"], "Very Common", "Easy"),
        ("Maximum Subarray", "Find the contiguous subarray with the largest sum (Kadane's Algorithm).", "Iterate through the array, maintaining current sum. Reset current sum to 0 if it becomes negative, and track max sum.", "Time Complexity: O(N), Space Complexity: O(1).", ["Arrays", "Dynamic Programming"], "Common", "Medium"),
        ("Insert Interval", "Insert a new interval into a sorted list of non-overlapping intervals and merge if necessary.", "Add all intervals before new interval, merge overlapping intervals with new interval, and add remaining.", "Time Complexity: O(N), Space Complexity: O(N) for output.", ["Arrays"], "Common", "Medium"),
        ("01 Matrix", "Find the distance of the nearest 0 for each cell in a binary matrix.", "Use BFS starting from all 0s simultaneously, updating neighbors with current distance + 1.", "Time Complexity: O(R * C), Space Complexity: O(R * C) for queue.", ["Graphs", "BFS"], "Common", "Medium"),
        ("K Closest Points to Origin", "Find the K closest points to the origin (0, 0) on a 2D plane.", "Use a max heap of size K to keep track of closest points, or use Quickselect.", "Time Complexity: O(N log K) with Max Heap, Space Complexity: O(K).", ["Heap", "Sorting"], "Common", "Medium"),
        ("Longest Substring Without Repeating Characters", "Find the length of the longest substring without repeating characters.", "Use sliding window with left and right pointers, and a hash set or map to store character indices.", "Time Complexity: O(N), Space Complexity: O(min(N, M)) where M is character set size.", ["Strings", "Sliding Window"], "Very Common", "Medium"),
        ("3Sum", "Find all unique triplets in an array that sum to zero.", "Sort the array, iterate and use two pointers for the remaining sum, skipping duplicates.", "Time Complexity: O(N^2) due to nested loops. Space Complexity: O(1) excluding sorting.", ["Arrays", "Two Pointers"], "Very Common", "Medium"),
        ("Binary Tree Level Order Traversal", "Return the level order traversal of its nodes' values.", "Use a queue for BFS, processing node levels by keeping track of queue size at each level.", "Time Complexity: O(N), Space Complexity: O(N) for queue.", ["Trees", "BFS"], "Very Common", "Medium"),
        ("Clone Graph", "Return a deep copy of a connected undirected graph.", "Use DFS or BFS with a hash map to map original nodes to their cloned counterparts.", "Time Complexity: O(V + E), Space Complexity: O(V) for map.", ["Graphs", "DFS", "BFS"], "Common", "Medium"),
        ("Evaluate Reverse Polish Notation", "Evaluate the value of an arithmetic expression in Reverse Polish Notation (postfix).", "Use a stack to store operands. Apply operators to the top two operands popped from stack.", "Time Complexity: O(N), Space Complexity: O(N).", ["Stack"], "Common", "Medium"),
        ("Course Schedule", "Determine if you can finish all courses given pre-requisites.", "Detect cycles in directed graph using Kahn's algorithm (BFS topological sort) or DFS.", "Time Complexity: O(V + E), Space Complexity: O(V + E).", ["Graphs", "Topological Sort"], "Very Common", "Medium"),
        ("Implement Trie (Prefix Tree)", "Implement a trie with insert, search, and startsWith methods.", "Use trie nodes containing an array of 26 children references and an isEndOfWord boolean flag.", "Insert/Search: O(L) where L is word length. Space Complexity: O(Alphabet * N * L).", ["Design", "Trie"], "Common", "Medium"),
        ("Coin Change", "Find the fewest number of coins that you need to make up a given amount.", "Use bottom-up Dynamic Programming tabulation. DP[i] = min(DP[i], DP[i - coin] + 1).", "Time Complexity: O(N * C) where C is amount and N is coin count. Space Complexity: O(C).", ["Dynamic Programming"], "Very Common", "Medium"),
        ("Product of Array Except Self", "Return an array output such that output[i] is equal to the product of all elements except nums[i] without division.", "Calculate prefix products and suffix products and multiply them into the result array.", "Time Complexity: O(N), Space Complexity: O(1) excluding output.", ["Arrays"], "Very Common", "Medium"),
        ("Min Stack", "Design a stack that supports push, pop, top, and retrieving the minimum element in O(1) time.", "Maintain a secondary stack that stores the minimum value seen so far corresponding to each element.", "Time Complexity: O(1) for all operations. Space Complexity: O(N).", ["Stack"], "Common", "Easy"),
        ("Validate Binary Search Tree", "Determine if a binary tree is a valid BST.", "Perform DFS, passing down minimum and maximum allowed range boundaries for each node.", "Time Complexity: O(N), Space Complexity: O(H).", ["Trees", "DFS"], "Very Common", "Medium"),
        ("Number of Islands", "Given an m x n 2D binary grid which represents a map of '1's (land) and '0's (water), return the number of islands.", "Iterate through cells. When land is found, increment island count and perform DFS/BFS to sink it.", "Time Complexity: O(R * C), Space Complexity: O(R * C) worst case.", ["Graphs", "DFS", "BFS"], "Very Common", "Medium"),
        ("Rotting Oranges", "Find the minimum time elapsed until all fresh oranges rot.", "Use multi-source BFS starting from all rotten oranges, updating adjacent fresh oranges level by level.", "Time Complexity: O(R * C), Space Complexity: O(R * C).", ["Graphs", "BFS"], "Common", "Medium"),
        ("Search in Rotated Sorted Array", "Search for a target value in a rotated sorted array in O(log N) time.", "Use binary search. Identify which half of the divided array is sorted, and check if target lies in its bounds.", "Time Complexity: O(log N), Space Complexity: O(1).", ["Binary Search"], "Very Common", "Medium"),
        ("Combination Sum", "Find all unique combinations of candidates that sum up to target.", "Use backtracking, sorting candidates to prune recursive paths when sum exceeds target.", "Time Complexity: O(2^T) where T is target, Space Complexity: O(T) recursion depth.", ["Backtracking"], "Common", "Medium"),
        ("Permutations", "Given an array nums of distinct integers, return all the possible permutations.", "Use backtracking to swap elements or maintain a boolean array of used elements recursively.", "Time Complexity: O(N * N!), Space Complexity: O(N) stack.", ["Backtracking"], "Very Common", "Medium"),
        ("Merge Intervals", "Given an array of intervals, merge all overlapping intervals.", "Sort the intervals by their start times, then iterate and merge overlapping ones with the last merged interval.", "Time Complexity: O(N log N) due to sorting, Space Complexity: O(N) or O(1) depending on sorting implementation.", ["Arrays"], "Very Common", "Medium"),
        ("Lowest Common Ancestor of a Binary Tree", "Find the lowest common ancestor (LCA) node of two given nodes in a binary tree.", "Recursively search left and right subtrees. If a node is found, return it. If both return non-null, current node is LCA.", "Time Complexity: O(N), Space Complexity: O(H).", ["Trees", "Recursion"], "Very Common", "Medium"),
        ("Time Based Key-Value Store", "Design a time-based key-value store that supports multiple values for the same key at different timestamps.", "Use a hash map mapping keys to a list of (timestamp, value) pairs. Use binary search on timestamps for get().", "Get: O(log N), Set: O(1). Space Complexity: O(N).", ["Design", "Binary Search"], "Common", "Medium"),
        ("Accounts Merge", "Merge accounts sharing common emails using Union-Find.", "Map emails to accounts and use Disjoint Set Union (DSU) to group accounts sharing emails.", "Time Complexity: O(N log N) with path compression, Space: O(N).", ["Graphs", "Union Find"], "Common", "Medium"),
        ("Sort Colors", "Sort an array of 0s, 1s, and 2s in-place (Dutch National Flag problem).", "Maintain three pointers: low, mid, and high. Swap elements to partition 0s at start and 2s at end.", "Time Complexity: O(N), Space Complexity: O(1).", ["Two Pointers", "Sorting"], "Common", "Medium"),
        ("Word Break", "Determine if a string s can be segmented into words from a dictionary.", "Use 1D Dynamic Programming. DP[i] represents if s[0...i] is segmentable. DP[i] = DP[j] && s[j...i] in dict.", "Time Complexity: O(N^2 * L) where L is max word length. Space: O(N).", ["Dynamic Programming"], "Common", "Medium"),
        ("Partition Equal Subset Sum", "Determine if an array can be partitioned into two subsets with equal sum.", "Check if total sum is even, then solve 0/1 Knapsack problem for target = sum / 2 using 1D array DP.", "Time Complexity: O(N * Sum), Space Complexity: O(Sum).", ["Dynamic Programming"], "Common", "Medium"),
        ("String to Integer (atoi)", "Implement the atoi function which converts a string to an integer.", "Discard whitespace, handle sign, read digits, handle integer overflow boundaries, and convert.", "Time Complexity: O(N), Space Complexity: O(1).", ["Strings", "Math"], "Common", "Medium"),
        ("Spiral Matrix", "Return all elements of an m x n matrix in spiral order.", "Use four boundary variables (top, bottom, left, right) and loop, updating boundaries after traversal.", "Time Complexity: O(R * C), Space Complexity: O(1) excluding output.", ["Arrays"], "Common", "Medium"),
        ("Subsets", "Given an integer array of unique elements, return all possible subsets (the power set).", "Use backtracking (decision tree: include / exclude element) or bitmasking.", "Time Complexity: O(N * 2^N), Space Complexity: O(N).", ["Backtracking"], "Common", "Medium"),
        ("Binary Tree Right Side View", "Return the values of the nodes you can see ordered from top to bottom from the right side of the tree.", "Use BFS (level order traversal) and collect the last element of each level, or DFS tracking max depth.", "Time Complexity: O(N), Space Complexity: O(D) where D is diameter.", ["Trees", "BFS", "DFS"], "Common", "Medium"),
        ("Longest Consecutive Sequence", "Find the length of the longest consecutive elements sequence in an unsorted array in O(N) time.", "Store all numbers in a hash set. Only count sequence lengths for numbers which represent the start of a sequence.", "Time Complexity: O(N), Space Complexity: O(N).", ["Arrays", "Hash Set"], "Common", "Medium"),
        ("Unique Paths", "Find the number of unique paths from top-left to bottom-right of an M x N grid.", "DP[i][j] = DP[i-1][j] + DP[i][j-1]. Can be optimized to use 1D array.", "Time Complexity: O(M * N), Space Complexity: O(N).", ["Dynamic Programming"], "Common", "Medium"),
        ("Single Number", "Find the single element in an array where every other element appears twice.", "XOR all elements in the array. Since X ^ X = 0 and X ^ 0 = X, the final result is the single number.", "Time Complexity: O(N), Space Complexity: O(1).", ["Bit Manipulation"], "Common", "Easy"),
        ("LRU Cache", "Design a Least Recently Used (LRU) Cache data structure.", "Use a Hash Map paired with a Doubly Linked List. Map maps keys to Doubly Linked List nodes for O(1) access.", "Time Complexity: O(1) for get and put. Space Complexity: O(Capacity).", ["Design", "Linked List"], "Very Common", "Medium"),
        ("Minimum Window Substring", "Find the minimum window in s containing all characters of t in O(N) time.", "Use sliding window with two pointers. Expand right pointer to find valid window; shrink left to minimize.", "Time Complexity: O(N), Space Complexity: O(K) for character map.", ["Strings", "Sliding Window"], "Common", "Hard"),
        ("Serialize and Deserialize Binary Tree", "Design an algorithm to serialize and deserialize a binary tree.", "Use preorder traversal (DFS) or level-order (BFS) with delimiters like '#' for null nodes.", "Time Complexity: O(N), Space Complexity: O(N).", ["Trees", "Design"], "Common", "Hard"),
        ("Trapping Rain Water", "Given n non-negative integers representing an elevation map where the width of each bar is 1, compute how much water it can trap.", "Use two pointers from left and right, tracking leftMax and rightMax to compute trapped water.", "Time Complexity: O(N), Space Complexity: O(1).", ["Two Pointers", "Stack"], "Very Common", "Hard"),
        ("Find Median from Data Stream", "Design a data structure that supports adding numbers and finding the median of the stream.", "Maintain a max-heap for the lower half and a min-heap for the upper half, keeping heap sizes balanced.", "Add: O(log N), Find Median: O(1). Space Complexity: O(N).", ["Design", "Heap"], "Common", "Hard"),
        ("Word Ladder", "Find the length of the shortest transformation sequence from beginWord to endWord.", "Use BFS on a graph where nodes are words and edges represent 1-character difference.", "Time Complexity: O(N * L^2) where L is word length and N is dictionary size. Space: O(N).", ["Graphs", "BFS"], "Common", "Hard"),
        ("Basic Calculator", "Implement a basic calculator to evaluate a simple expression string containing brackets, addition, and subtraction.", "Use a stack to push current result and sign when encountering an opening bracket, and pop on closing.", "Time Complexity: O(N), Space Complexity: O(N).", ["Stack", "Strings"], "Common", "Hard"),
        ("Maximum Profit in Job Scheduling", "Find the maximum profit you can achieve by scheduling non-overlapping jobs.", "Sort jobs by end time. Use Dynamic Programming with Binary Search (bisect) to find last non-overlapping job.", "Time Complexity: O(N log N) due to sorting & binary search. Space: O(N).", ["Dynamic Programming", "Binary Search"], "Common", "Hard"),
        ("Merge k Sorted Lists", "Merge K sorted linked lists and return it as one sorted list.", "Use a min-heap (Priority Queue) storing the head nodes of all lists, popping the smallest and inserting its next.", "Time Complexity: O(N log K) where N is total nodes. Space Complexity: O(K).", ["Linked List", "Heap"], "Very Common", "Hard"),
        ("Largest Rectangle in Histogram", "Find the area of the largest rectangle in the histogram.", "Use a monotonic increasing stack to store indices, calculating rectangle area when popping elements.", "Time Complexity: O(N), Space Complexity: O(N).", ["Stack"], "Common", "Hard"),
        ("Edit Distance", "Find the minimum number of operations required to convert word1 to word2.", "Use 2D Dynamic Programming. Operations: Insert, Delete, Replace. DP[i][j] represents edits for word1[0...i] and word2[0...j].", "Time Complexity: O(M * N), Space Complexity: O(M * N) or O(N).", ["Dynamic Programming"], "Common", "Hard"),
        ("Minimum Path Sum", "Find a path from top-left to bottom-right of a grid which minimizes the sum of all numbers along its path.", "DP[i][j] = grid[i][j] + min(DP[i-1][j], DP[i][j-1]) (in-place modification).", "Time Complexity: O(R * C), Space Complexity: O(1).", ["Dynamic Programming"], "Common", "Medium"),
        ("House Robber", "Determine the maximum amount of money you can rob tonight without alerting the police.", "DP[i] = max(DP[i-1], DP[i-2] + house[i]). Can be optimized using two variables.", "Time Complexity: O(N), Space Complexity: O(1).", ["Dynamic Programming"], "Very Common", "Medium"),
        ("Kth Largest Element in an Array", "Find the kth largest element in an unsorted array.", "Use a min-heap of size K, or use Quickselect algorithm.", "Time Complexity: O(N log K) with min-heap, or O(N) average with Quickselect. Space: O(K).", ["Heap", "Divid and Conquer"], "Common", "Medium"),
        ("Daily Temperatures", "Given an array of temperatures, return an array answers where answers[i] is the number of days you have to wait for a warmer temp.", "Use a monotonic decreasing stack to store indices. Pop when finding a warmer temperature.", "Time Complexity: O(N), Space Complexity: O(N).", ["Stack"], "Common", "Medium"),
        ("Subarray Sum Equals K", "Find the total number of continuous subarrays whose sum equals to K.", "Use a prefix sum hash map that stores the frequency of all prefix sums observed so far.", "Time Complexity: O(N), Space Complexity: O(N).", ["Arrays", "Hash Map"], "Common", "Medium"),
        ("Decode String", "Given an encoded string, return its decoded string (e.g. 3[a]2[bc] -> aaabcbc).", "Use two stacks: one for count multipliers and one for current string buffers.", "Time Complexity: O(N), Space Complexity: O(N).", ["Stack", "Strings"], "Common", "Medium"),
        ("Top K Frequent Elements", "Given an integer array nums and an integer k, return the k most frequent elements.", "Count frequencies with a hash map. Use bucket sort or a min-heap of size K.", "Time Complexity: O(N) with bucket sort, Space Complexity: O(N).", ["Hash Map", "Heap"], "Common", "Medium"),
        ("Letter Combinations of a Phone Number", "Return all possible letter combinations that the number could represent from a phone keypad.", "Use backtracking to recursively append letters corresponding to each digit.", "Time Complexity: O(4^N), Space Complexity: O(N) recursion stack.", ["Backtracking", "Strings"], "Common", "Medium"),
        ("Generate Parentheses", "Generate all combinations of well-formed parentheses given n pairs.", "Use backtracking, tracking open and close bracket counts. Add open if open < n; add close if close < open.", "Time Complexity: O(4^N / sqrt(N)), Space: O(N).", ["Backtracking"], "Common", "Medium"),
        ("Longest Common Subsequence", "Find the length of the longest common subsequence between two strings.", "Use 2D Dynamic Programming table. If s1[i] == s2[j], DP[i][j] = 1 + DP[i-1][j-1]; else max(DP[i-1][j], DP[i][j-1]).", "Time Complexity: O(M * N), Space Complexity: O(M * N).", ["Dynamic Programming"], "Common", "Medium"),
        ("Word Search", "Determine if a word exists in a 2D grid of characters.", "Use backtracking DFS starting from each cell in the grid, marking visited cells in-place.", "Time Complexity: O(R * C * 4^L) where L is word length. Space: O(L) call stack.", ["Backtracking", "Matrix"], "Common", "Medium")
    ]
    
    # 2. DBMS (50 unique questions)
    dbms_list = [
        ("ACID Properties", "Explain the ACID properties of database transactions.", "ACID stands for Atomicity (all-or-nothing), Consistency (integrity constraints), Isolation (independent concurrency), and Durability (persistence).", "Essential for transactional reliability. Implemented via locks, WAL (Write-Ahead Log), and undo/redo logs.", ["ACID", "Transactions"], "Very Common", "Medium"),
        ("Database Normalization", "What is normalization and describe 1NF, 2NF, 3NF, and BCNF.", "Normalization is structuring relational tables to reduce data redundancy and eliminate anomalies.", "1NF: Atomic values; 2NF: No partial dependencies; 3NF: No transitive dependencies; BCNF: X must be superkey for X -> Y.", ["Normalization"], "Very Common", "Medium"),
        ("Primary Key vs Unique Key", "What is the difference between a primary key and a unique key?", "Primary key uniquely identifies a row and cannot be null. Unique key also ensures uniqueness but allows one null value.", "Only one Primary key per table. Multiple unique keys are allowed. Under the hood, both create B-tree indexes.", ["Primary Key", "Constraints"], "Common", "Easy"),
        ("Indexes: Clustered vs Non-Clustered", "Explain clustered and non-clustered indexes.", "Clustered index determines the physical order of data pages (one per table). Non-clustered index is a separate structure mapping keys to row addresses.", "Clustered index leaf node contains actual data. Non-clustered contains pointer. Clustered is faster for range queries.", ["Indexing"], "Very Common", "Medium"),
        ("B-Tree vs Hash Indexes", "When do you use a B-Tree index versus a Hash index?", "B-Tree supports range and sorting queries (<, >, BETWEEN). Hash index only supports equality checks (=) in O(1) time.", "B-Tree keeps data sorted in leaf nodes. Hash index uses hashing functions which are faster but don't support ranges.", ["Indexing", "Hash Map"], "Common", "Medium"),
        ("Database Sharding vs Partitioning", "What is the difference between database sharding and partitioning?", "Partitioning splits a table within a single database instance. Sharding splits the dataset across multiple independent database nodes.", "Partitioning can be horizontal or vertical. Sharding scales write throughput horizontally by distributing load across servers.", ["Sharding", "Scalability"], "Very Common", "Hard"),
        ("Replication Models", "Compare Master-Slave and Multi-Master database replication.", "Master-Slave: All writes go to Master, replicated to Slaves for reads. Multi-Master: Writes go to any node, resolved conflict-free.", "Master-Slave scales reads but has master bottleneck. Multi-Master has complex write conflict resolution.", ["Replication", "System Design"], "Common", "Medium"),
        ("CAP Theorem", "Explain the CAP Theorem and its application to databases.", "A distributed system can guarantee at most two out of three: Consistency, Availability, and Partition Tolerance.", "In practice, network partitions (P) are inevitable, so systems must choose between Consistency (C) or Availability (A).", ["CAP Theorem", "Distributed Systems"], "Very Common", "Medium"),
        ("NoSQL vs SQL", "Compare SQL and NoSQL databases.", "SQL: Relational, structured schema, scales vertically, ACID compliant. NoSQL: Non-relational, dynamic schema, scales horizontally, eventual consistency.", "Use SQL for structured transaction-heavy data. Use NoSQL for unstructured, high-write, and scalable datasets.", ["NoSQL", "SQL"], "Very Common", "Medium"),
        ("Database Isolation Levels", "Explain the four ANSI SQL transaction isolation levels.", "Read Uncommitted, Read Committed, Repeatable Read, and Serializable.", "Read Uncommitted allows dirty reads. Read Committed prevents dirty reads. Repeatable Read prevents non-repeatable. Serializable prevents phantom reads.", ["Transactions", "Concurrency"], "Very Common", "Hard"),
        ("Concurrency Anomalies", "Explain Dirty Reads, Non-Repeatable Reads, and Phantom Reads.", "Dirty Read: Reading uncommitted data. Non-Repeatable: Reading same row twice, getting different data. Phantom: Querying rows twice, getting new rows.", "These are concurrency anomalies that occur when isolation levels are lower than Serializable.", ["Concurrency", "Transactions"], "Common", "Medium"),
        ("Optimistic vs Pessimistic Locking", "When would you choose Optimistic Locking over Pessimistic Locking?", "Optimistic: Assume no conflict, check version column on write. Pessimistic: Lock rows using SELECT FOR UPDATE.", "Optimistic is best for high-read, low-write scenarios. Pessimistic is best for high-contention, finance transactions.", ["Locking", "Concurrency"], "Very Common", "Medium"),
        ("Shared vs Exclusive Locks", "Explain Shared (S) and Exclusive (X) locks.", "Shared Lock: Multiple transactions can read. Exclusive Lock: Only one transaction can write, blocks all others.", "Read locks are shared. Write locks are exclusive. An exclusive lock conflicts with both shared and exclusive.", ["Locking"], "Common", "Medium"),
        ("Explain Plan", "What is an EXPLAIN PLAN and how does it help query optimization?", "EXPLAIN PLAN shows the execution pathway selected by the query optimizer (e.g. Sequential Scan vs Index Scan).", "Helps identify missing indexes, table scans, sorting overhead, and join performance bottlenecks.", ["Query Optimization"], "Common", "Medium"),
        ("Connection Pooling", "Why do databases use connection pooling?", "Reusing active database connections to avoid the heavy cost of repeatedly creating and destroying TCP sockets.", "Frameworks like HikariCP manage a pool of active connections, yielding significant response latency gains.", ["Performance"], "Common", "Medium"),
        ("Write-Ahead Logging (WAL)", "What is Write-Ahead Logging (WAL) in databases?", "WAL ensures that changes are written to a append-only log file on disk before updating the actual database pages.", "Guarantees durability (D in ACID) and crash recovery, as the database can replay log transactions on reboot.", ["Recovery", "ACID"], "Common", "Medium"),
        ("Foreign Keys Performance", "How do foreign key constraints affect write performance?", "Foreign keys require checking referential integrity on every insert/update, causing implicit read overhead on referenced tables.", "To optimize, indexes should always be added to foreign key columns, which speeds up checks and joins.", ["Performance", "Constraints"], "Common", "Medium"),
        ("View vs Materialized View", "Explain the difference between a View and a Materialized View.", "View: A virtual table representing a query; executed on the fly. Materialized View: Query result physically cached on disk.", "Materialized Views speed up expensive aggregation queries but require refresh strategies (manual or trigger-based).", ["Database Objects"], "Common", "Medium"),
        ("Redo vs Undo Logs", "What is the difference between Redo and Undo logs?", "Redo: Replays committed transactions for durability. Undo: Reverts uncommitted changes for transaction rollback.", "Redo logs write forward. Undo logs write backward, facilitating MVCC (Multi-Version Concurrency Control).", ["Recovery", "Transactions"], "Common", "Medium"),
        ("SQL Injection Prevention", "How do you prevent SQL Injection vulnerabilities?", "Use Prepared Statements (Parametric Queries) or Object Relational Mappers (ORMs). Avoid string concatenation.", "Prepared statements compile SQL command structure first, treating user input strictly as parameters, not executable code.", ["Security"], "Very Common", "Easy"),
        ("SQL Joins", "Explain Inner Join, Left Join, and Full Outer Join.", "Inner: Matching rows in both tables. Left: All rows from left table, matching from right. Full Outer: All rows from both tables.", "Right Join is left join with tables swapped. Null values fill missing columns in left/right joins.", ["SQL"], "Very Common", "Easy"),
        ("Group By vs Partition By", "What is the difference between GROUP BY and PARTITION BY?", "GROUP BY collapses multiple rows into a single summary row. PARTITION BY is a window function that keeps individual rows.", "GROUP BY reduces row count. PARTITION BY computes running totals/ranks over windows without collapsing rows.", ["SQL"], "Common", "Medium"),
        ("DBMS Deadlocks", "How do database engines handle deadlocks?", "Database engines run background deadlock detection loops that scan wait-for graphs and abort one transaction.", "Aborted transactions rollback, releasing their locks. Developers can avoid deadlocks by updating tables in a consistent order.", ["Locking", "Concurrency"], "Common", "Medium"),
        ("Database Migrations", "Why are database migration tools like Flyway or Liquibase used?", "They manage and apply version-controlled schema modifications sequentially across different environment environments.", "Maintains schema parity across Local, Staging, and Production databases, avoiding manual execution failures.", ["DevOps"], "Common", "Medium"),
        ("Horizontal vs Vertical Scaling", "Compare database horizontal and vertical scaling.", "Vertical: Upgrading CPU/RAM/Disk of a single node. Horizontal: Adding more database nodes (read replicas/shards).", "Vertical has physical limits and single point of failure. Horizontal is elastic but adds network latency and synchronization issues.", ["Scalability"], "Common", "Medium"),
        ("MVCC", "What is Multi-Version Concurrency Control (MVCC)?", "MVCC allows readers and writers to access data concurrently without locking. Readers see a snapshot version of data.", "Implemented by keeping multiple row versions. PostgreSQL uses transaction IDs (xmin, xmax) for visibility check.", ["Concurrency", "Transactions"], "Common", "Hard"),
        ("Cassandra LSM Trees", "Why does Apache Cassandra use Log-Structured Merge (LSM) Trees?", "LSM Trees optimize write throughput by writing sequentially to memory (Memtable) and flushing to files (SSTables) on disk.", "Avoids random disk seeks. High-speed writes are merged and sorted asynchronously via compaction loops.", ["Cassandra", "NoSQL"], "Common", "Hard"),
        ("Redis Persistence", "Explain RDB and AOF persistence models in Redis.", "RDB: Point-in-time snapshot of dataset saved to disk. AOF: Append-only log of every write operation received.", "RDB is fast for restarts but loses data since last snapshot. AOF is durable but creates larger files and slower starts.", ["Redis", "Caching"], "Common", "Medium"),
        ("ElasticSearch Sharding", "What are primary and replica shards in ElasticSearch?", "Primary shards store data and distribute indices. Replica shards provide read scaling and hardware fault-tolerance.", "Replica shards are copies of primary shards. If a primary shard node fails, a replica is promoted to primary.", ["ElasticSearch", "Search Index"], "Common", "Hard"),
        ("DynamoDB Partition Keys", "How does DynamoDB route queries using Partition Keys?", "DynamoDB hashes the Partition Key to determine the physical partition where the item is stored.", "To prevent hot spots, partition keys must have high cardinality (e.g. user_id rather than country).", ["DynamoDB", "NoSQL"], "Common", "Hard"),
        ("MongoDB Replica Sets", "What is a MongoDB Replica Set?", "A group of mongod processes that maintain the same data set, providing high availability and redundancy.", "Consists of one Primary node (writes) and multiple Secondaries. Heartbeats elect a new primary if primary fails.", ["MongoDB", "NoSQL"], "Common", "Medium"),
        ("Database Denormalization", "When and why would you denormalize a database?", "To optimize read performance in read-heavy applications, by adding redundant columns to avoid expensive SQL joins.", "Reduces read latency but requires application-level logic to maintain consistency across duplicate records.", ["Performance"], "Common", "Medium"),
        ("Common Table Expressions (CTE)", "What is a CTE and why is it useful?", "A temporary named result set defined within a SELECT statement, written using the WITH keyword.", "Improves readability of complex nested queries. Can be recursive, allowing graph and hierarchical queries.", ["SQL"], "Common", "Easy"),
        ("Database Triggers", "What are database triggers and their drawbacks?", "Automated blocks of SQL code executed in response to database events (INSERT, UPDATE, DELETE).", "Drawbacks: Implicit execution makes debugging difficult, decreases write performance, and hides business logic.", ["Database Objects"], "Common", "Medium"),
        ("Stored Procedures", "What are stored procedures and their pros/cons?", "Compiled SQL modules stored in the database database server, executed by calling their name.", "Pros: Network savings, security. Cons: Vendor lock-in, hard to unit test, increases database CPU load.", ["Database Objects"], "Common", "Medium"),
        ("Index Fragmentation", "What is index fragmentation and how do you resolve it?", "Occurs when data insertions/updates split pages, causing B-tree leaf nodes to be out of physical order on disk.", "Resolved by REBUILDING or REORGANIZING the index, reclaiming unused page space and sorting node sequences.", ["Indexing"], "Common", "Medium"),
        ("Replication Lag", "What causes replication lag and how do you mitigate it?", "Occurs when replica nodes cannot write changes as fast as master node receives them, often due to network latency or lock contention.", "Mitigated by scaling replica disk write I/O, using parallel replication threads, or optimizing queries.", ["Replication"], "Common", "Hard"),
        ("Two-Phase Commit (2PC)", "Explain the Two-Phase Commit protocol.", "A distributed transaction consensus protocol containing a Prepare phase and a Commit phase.", "Coordinator asks participants if they can commit. If all reply Yes, coordinator broadcasts Commit; else Rollback.", ["Transactions", "Distributed Systems"], "Common", "Hard"),
        ("Saga Pattern", "How does the Saga Pattern handle distributed transaction consistency?", "Breaks a transaction into local steps. If a step fails, compensation transactions are executed in reverse order to rollback state.", "Can be Choreography-based (event-driven) or Orchestration-based (central coordinator service). Avoids locking resources.", ["Distributed Systems", "Transactions"], "Very Common", "Hard"),
        ("Columnar Databases", "Compare Columnar and Row-oriented databases.", "Row-oriented stores row values adjacent on disk (OLTP). Columnar stores column values adjacent on disk (OLAP).", "Row-oriented is optimal for CRUD operations. Columnar is optimal for analytical aggregations (SUM, AVG) over large tables.", ["OLAP", "OLTP"], "Common", "Hard"),
        ("Eventual Consistency", "What is Eventual Consistency?", "A consistency model in distributed databases where replica updates sync asynchronously. If no writes occur, all replicas eventually match.", "Improves availability and write throughput (Base model), but reads can briefly return stale data.", ["Consistency", "CAP Theorem"], "Common", "Medium"),
        ("PostgreSQL VACUUM", "Why does PostgreSQL require the VACUUM command?", "PostgreSQL uses MVCC. Dead rows from updates/deletes remain on disk. VACUUM reclaims page space of dead rows.", "Autovacuum runs in background, but high-write tables sometimes require manual VACUUM ANALYZE to update statistics.", ["PostgreSQL"], "Common", "Hard"),
        ("Database Backups", "Compare Logical and Physical backups.", "Logical: SQL script containing table structure and INSERT data (e.g. pg_dump). Physical: Copying binary database files on disk.", "Logical is portable but slow. Physical is fast to restore and backup but environment-locked.", ["Recovery"], "Common", "Medium"),
        ("PostgreSQL JSONB", "When should you use JSONB columns in PostgreSQL?", "Use JSONB for semi-structured data where schemas change frequently, or for dictionary tags.", "JSONB parses strings into binary, allowing indexing (GIN) on nested keys. Regular JSON only stores text strings.", ["PostgreSQL"], "Common", "Medium"),
        ("Connection Leaks", "What causes database connection leaks and how do you trace them?", "Occurs when code opens a database connection but fails to close it (e.g. missing finally block). Traced using leak detection logs in connection pools.", "Tracing utilities (e.g. Hikari leakDetectionThreshold) print stack traces of threads holding connections too long.", ["Performance"], "Common", "Medium"),
        ("NoSQL Types", "Explain the four main types of NoSQL databases.", "Document (MongoDB), Key-Value (Redis), Wide-Column (Cassandra), and Graph (Neo4j).", "Choose Document for general entities, Key-Value for caching, Wide-Column for time-series, and Graph for connections.", ["NoSQL"], "Common", "Medium"),
        ("Composite Index Leftmost Prefix", "Explain the leftmost prefix rule in composite indexes.", "A composite index on (A, B) can optimize queries using (A) or (A, B), but NOT queries using only (B).", "Database searches index starting with the first column. Skipping the first column makes the index search invalid.", ["Indexing"], "Common", "Medium"),
        ("Hot Spot Partitioning", "How do you avoid hot spot partitions in DynamoDB?", "Use partition keys with high cardinality and distribute write volume by appending a random suffix identifier if writing same key.", "Ensures hashing function distributes write workload evenly across all partition servers.", ["DynamoDB", "NoSQL"], "Common", "Hard"),
        ("Redis Sentinel vs Cluster", "Compare Redis Sentinel and Redis Cluster.", "Sentinel: High-availability system providing monitoring, alerts, and automatic master failover. Cluster: Sharding system across multiple nodes.", "Sentinel is master-slave setup (non-sharded). Cluster is sharded and scales write throughput horizontally.", ["Redis", "Caching"], "Common", "Hard"),
        ("Index Cardinality", "What is Index Cardinality and why does it matter?", "Cardinality is the uniqueness of values in a column. High cardinality (IDs) vs Low cardinality (Genders).", "Query optimizers avoid using indexes on low cardinality columns, as table scans are more efficient.", ["Indexing"], "Common", "Medium")
    ]
    
    # 3. OS (50 unique questions)
    os_list = [
        ("Process vs Thread", "Explain the difference between a process and a thread.", "Process is an executing instance of a program with separate memory. Thread is a path of execution inside a process sharing memory.", "Processes are heavy-weight, protected from each other. Threads are light-weight, sharing heap space but having independent stacks.", ["Processes", "Threads"], "Very Common", "Medium"),
        ("Deadlock Conditions", "What is a Deadlock and what are the four Coffman conditions?", "Deadlock is a state where processes are blocked waiting for resources held by each other.", "Conditions: Mutual Exclusion, Hold and Wait, No Preemption, and Circular Wait. All four must hold for a deadlock to occur.", ["Deadlocks"], "Very Common", "Medium"),
        ("Semaphores vs Mutexes", "What is the difference between a Semaphore and a Mutex?", "Mutex is a locking mechanism (binary) with ownership. Semaphore is a signaling mechanism (counter) without ownership.", "Only the thread that locks a Mutex can unlock it. Any thread can increment/signal a Semaphore to release blocked threads.", ["Concurrency", "Synchronization"], "Very Common", "Medium"),
        ("CPU Scheduling", "Explain SJF, Round Robin, and Priority scheduling algorithms.", "SJF: Schedules job with shortest CPU burst next. Round Robin: Allocates fixed time slices sequentially. Priority: Schedules highest priority job.", "SJF minimizes average waiting times. Round Robin ensures fairness and avoids starvation but context-switches often.", ["Scheduling"], "Common", "Medium"),
        ("Virtual Memory & Paging", "Explain Virtual Memory and Paging.", "Virtual Memory simulates physical RAM by using secondary storage. Paging maps virtual address pages to physical memory frames.", "Page table maps virtual addresses to physical. Enables running programs larger than physical memory space.", ["Memory Management"], "Very Common", "Medium"),
        ("Page Replacement", "What is a Page Fault and explain the LRU page replacement algorithm.", "Page Fault: CPU requests a page not loaded in RAM. LRU (Least Recently Used) evicts the page that has not been accessed the longest.", "LRU requires tracking page access history. Implemented using a queue/stack or aging registers.", ["Memory Management"], "Common", "Medium"),
        ("Thread Safety", "What makes code Thread-Safe and what is a Race Condition?", "Thread-safe code operates correctly when accessed by multiple threads. Race condition occurs when output depends on execution order.", "Race conditions occur on unsynchronized access to shared mutable state. Resolved using locks, atomic variables, or monitors.", ["Concurrency"], "Very Common", "Medium"),
        ("Context Switching", "Explain what happens during a context switch.", "CPU stops executing current process, saves registers/state in PCB, and loads register states of new process from its PCB.", "Context switching incurs CPU cache flushing and page table reloading overhead, making process switches heavier than thread switches.", ["Processes", "CPU"], "Common", "Medium"),
        ("Inter-Process Communication", "Explain the different models of IPC.", "Shared Memory, Message Passing (Message Queues), Sockets, and Pipes.", "Shared memory is fastest as it avoids system calls once mapped. Message passing is safer as OS manages buffers.", ["IPC"], "Common", "Medium"),
        ("Thrashing", "What is Thrashing in Operating Systems?", "A state where the CPU spends more time swapping pages in and out of disk than executing instructions, due to lack of RAM.", "Occurs when total working set sizes of active processes exceed physical RAM. Mitigated by terminating processes.", ["Memory Management"], "Common", "Medium"),
        ("User vs Kernel Mode", "What is the difference between User Mode and Kernel Mode?", "User Mode: Restricted execution mode for user applications. Kernel Mode: Privileged execution mode with full hardware access.", "Applications run in user mode and switch to kernel mode via system calls when requesting OS resources.", ["System Design"], "Common", "Medium"),
        ("System Calls", "What is a System Call and how does it work?", "A system call is the programmatic interface provided by the OS that allows user-mode programs to request kernel-mode services.", "Triggers a software interrupt (trap), switching CPU execution state to kernel mode to run the corresponding handler.", ["OS Basics"], "Common", "Medium"),
        ("Memory Fragmentation", "Compare Internal and External Memory Fragmentation.", "Internal: Allocated memory block is larger than requested data, leaving unused space. External: Free memory is split into small non-contiguous blocks.", "Internal occurs in fixed paging. External occurs in variable-sized segmentation. Resolved via paging or compaction.", ["Memory Management"], "Common", "Medium"),
        ("Segmentation", "What is Segmentation in memory management?", "A memory management scheme that divides virtual memory into logical, variable-sized segments (e.g. Code, Stack, Heap).", "Each segment has a base address and limit. Provides logical separation but suffers from external fragmentation.", ["Memory Management"], "Common", "Medium"),
        ("DLL vs Static Library", "Compare Dynamic Link Libraries (DLL) and Static Libraries.", "Static: Library code compiled directly into application binary. DLL: Linked dynamically at runtime, shared across processes in RAM.", "Static creates larger binaries but runs self-contained. DLLs save memory but suffer from dependency version conflicts.", ["OS Basics"], "Common", "Medium"),
        ("Monolithic vs Microkernel", "Compare Monolithic and Microkernel architectures.", "Monolithic: All OS services (drivers, file system) run in kernel space. Microkernel: Minimal kernel, services run in user space.", "Monolithic is faster but failure crashes OS. Microkernel is modular and secure but slower due to IPC overhead.", ["System Design"], "Common", "Hard"),
        ("Fork System Call", "How does the fork() system call work?", "fork() creates a duplicate child process. It returns 0 in the child process, and returns the child's PID in the parent process.", "Uses Copy-on-Write (COW) optimization so parent and child share physical memory pages until one modifies them.", ["Processes"], "Common", "Medium"),
        ("Zombie vs Orphan Processes", "What are Zombie and Orphan processes?", "Zombie: Finished process whose parent hasn't read its exit status yet. Orphan: Running process whose parent has terminated.", "Zombies consume PID slots. Orphans are adopted by the init process (PID 1) which cleans up their state.", ["Processes"], "Common", "Medium"),
        ("Cache Coherence", "What is Cache Coherence in multi-core systems?", "Ensures that multiple cores accessing shared memory don't read stale data from their local L1/L2 hardware caches.", "Resolved using cache coherence protocols like MESI (Modified, Exclusive, Shared, Invalid) to invalidate outdated cache lines.", ["CPU Architecture"], "Common", "Hard"),
        ("Inodes", "What is an inode in Unix-like file systems?", "An inode (index node) is a data structure storing file metadata (permissions, owner, size) and pointers to data blocks on disk.", "Does not store file name. File names map to inode numbers in directory structures.", ["File Systems"], "Common", "Medium"),
        ("RAID Levels", "Explain RAID 0, RAID 1, and RAID 5.", "RAID 0: Striping (performance, no redundancy). RAID 1: Mirroring (redundancy, no size gain). RAID 5: Block-level striping with distributed parity.", "RAID 0 is for speed. RAID 1 is for fault-tolerance. RAID 5 allows recovery of one disk failure with parity overhead.", ["Storage"], "Common", "Medium"),
        ("Critical Section Problem", "What is the Critical Section problem and its requirements?", "A region of code accessing shared resources that must not be concurrently accessed by multiple threads.", "Requirements: Mutual Exclusion (only one), Progress (no block), and Bounded Waiting (no starvation).", ["Concurrency"], "Common", "Medium"),
        ("Peterson's Solution", "Explain Peterson's Solution for critical sections.", "A classic software-based solution for two threads using a turn variable and a flag array.", "Guarantees mutual exclusion and progress but relies on sequential consistency, which modern CPUs out-of-order execution violates.", ["Concurrency"], "Common", "Hard"),
        ("Spinlocks", "What is a Spinlock and when is it used?", "A lock where a thread loops continuously ('spins') checking if the lock is available, rather than sleeping.", "Saves thread context-switch sleep overhead. Optimal for short wait times, commonly used in kernel development.", ["Concurrency"], "Common", "Medium"),
        ("Starvation vs Deadlock", "What is the difference between Starvation and Deadlock?", "Deadlock: Processes are locked waiting for each other, none can progress. Starvation: Process is ready but never gets scheduled.", "Deadlocks involve circular dependency blocks. Starvation occurs due to unfair scheduling policies (e.g. priority queues).", ["Scheduling", "Concurrency"], "Common", "Medium"),
        ("Memory-Mapped Files", "What is memory-mapping (mmap) and its benefits?", "Maps a file on disk directly into a process's virtual address space, allowing file access via memory pointers.", "Avoids system call read/write buffers, yielding high performance for large file reading and writing.", ["Memory Management"], "Common", "Medium"),
        ("Spooling", "What is Spooling in operating systems?", "SPOOL (Simultaneous Peripheral Operations On-Line) buffers data for slow devices (like printers) on disk until ready.", "Prevents fast CPUs from blocking on slow hardware transfers. Manages print queues seamlessly.", ["I/O Devices"], "Common", "Easy"),
        ("FAT vs NTFS", "Compare FAT and NTFS file systems.", "FAT: Simple table allocation, lacks security, file size limit (4GB). NTFS: Modern journaling file system, supports encryption and permissions.", "NTFS tracks changes in journals to prevent file corruption on power loss. FAT is used for USB portability.", ["File Systems"], "Common", "Medium"),
        ("Bootstrapping", "What is bootstrapping (booting process)?", "On power, BIOS/UEFI initializes hardware, loads Boot Loader from MBR to RAM, which then loads Kernel into memory.", "Kernel initializes OS data structures, device drivers, and starts the first user process (init/systemd).", ["OS Basics"], "Common", "Medium"),
        ("Kernel Panic", "What is a Kernel Panic or Blue Screen of Death?", "An action taken by an operating system when it detects a critical internal error from which it cannot safely recover.", "Prints debugging info, stops CPU cores, and syncs disks to prevent file corruption.", ["OS Basics"], "Common", "Easy"),
        ("Multiprocessing vs Multithreading", "Compare Multiprocessing and Multithreading.", "Multiprocessing: Running multiple processes (independent memory). Multithreading: Running multiple threads (shared memory).", "Multiprocessing is fault-tolerant (crash is isolated) but context switches are slow. Multithreading is fast but crash kills process.", ["Processes", "Threads"], "Common", "Medium"),
        ("Interrupts vs Polling", "Compare Interrupts and Polling for device communication.", "Polling: CPU checks device status registers continuously. Interrupts: Device signals CPU when data is ready.", "Polling wastes CPU cycles. Interrupts allow CPU to do other work, suspending tasks only when hardware triggers inputs.", ["I/O Devices"], "Common", "Medium"),
        ("Thread Pools", "Why do applications use Thread Pools?", "Reuses a queue of worker threads to process tasks, avoiding the high cost of creating and destroying OS threads repeatedly.", "Controls thread saturation limits, preventing system CPU exhaustion from spawning thousands of threads.", ["Concurrency"], "Common", "Medium"),
        ("Concurrency vs Parallelism", "What is the difference between Concurrency and Parallelism?", "Concurrency: Handling multiple tasks at once by interleaving them. Parallelism: Executing multiple tasks simultaneously.", "Concurrency can run on a single core via scheduling. Parallelism requires multi-core CPU architectures.", ["Concurrency"], "Common", "Medium"),
        ("Amdahl's Law", "What is Amdahl's Law and its significance?", "Calculates the maximum speedup limit of a program using parallel processors, constrained by its sequential components.", "Speedup = 1 / (S + (1 - S)/N) where S is sequential fraction. Emphasizes that parallel scaling is bounded by serial blocks.", ["Performance"], "Common", "Hard"),
        ("Translation Lookaside Buffer (TLB)", "What is a TLB and how does it optimize virtual memory?", "A hardware cache in the MMU that stores recent virtual-to-physical address mappings.", "Saves expensive double-lookup memory accesses to page tables, accelerating memory access times.", ["CPU Architecture"], "Common", "Hard"),
        ("Copy-on-Write (COW)", "Explain Copy-on-Write (COW) memory optimization.", "Allows multiple processes to share same memory pages until one process writes, at which point a page copy is created.", "Optimizes fork() system calls. Child processes share parent memory until writes occur, avoiding redundant memory copying.", ["Memory Management"], "Common", "Medium"),
        ("Page Size Tradeoffs", "What are the trade-offs of large page sizes in virtual memory?", "Large pages: Smaller page tables, fewer TLB misses, faster I/O. Drawback: Increases internal fragmentation.", "Smaller pages use memory efficiently but require large page table structures and increase page fault frequencies.", ["Memory Management"], "Common", "Hard"),
        ("Swapping", "What is Swapping in memory management?", "Temporarily moving inactive processes out of physical RAM to swap space on disk to free up memory.", "Allows active processes to allocate enough RAM, but brings disk read overhead when swapped processes resume.", ["Memory Management"], "Common", "Medium"),
        ("Process Control Block (PCB)", "What metadata does a Process Control Block (PCB) contain?", "Contains Process ID (PID), Process State (Ready, Run), Program Counter (PC), CPU registers, memory limits, and open file lists.", "Acts as the repository of process context saved during CPU context switches.", ["Processes"], "Common", "Medium"),
        ("Thread Control Block (TCB)", "What is a Thread Control Block (TCB) and how does it differ from a PCB?", "A TCB stores thread-specific metadata: Thread ID, Stack Pointer, Program Counter, and registers.", "TCB is lighter. Threads share heap and global files stored in the parent's PCB, keeping TCB size minimal.", ["Threads"], "Common", "Medium"),
        ("Schedulers types", "What is the difference between Long-term, Medium-term, and Short-term schedulers?", "Long-term (Job): Controls degree of multiprogramming. Short-term (CPU): Selects next process to run. Medium-term: Swaps processes.", "Long-term runs slow, picking tasks from disk. Short-term runs in milliseconds, allocating CPU time slots.", ["Scheduling"], "Common", "Medium"),
        ("Preemptive Scheduling", "Compare Preemptive and Non-Preemptive scheduling.", "Preemptive: OS can interrupt a running process to run another. Non-Preemptive: Process runs until it yields or terminates.", "Preemptive ensures responsiveness (time-sharing) but requires concurrency synchronization. Non-Preemptive is simple but causes starvation.", ["Scheduling"], "Common", "Medium"),
        ("Priority Inversion", "What is Priority Inversion and how is it resolved?", "Occurs when a low-priority thread holds a lock needed by a high-priority thread, while a medium-priority thread blocks execution.", "Resolved using Priority Inheritance: low-priority thread temporarily inherits high priority until it releases the lock.", ["Concurrency", "Scheduling"], "Common", "Hard"),
        ("Belady's Anomaly", "What is Belady's Anomaly and when does it occur?", "An anomaly where increasing the number of page frames results in more page faults.", "Occurs in FIFO page replacement algorithm. Does not occur in stack-based algorithms like LRU.", ["Memory Management"], "Common", "Medium"),
        ("Direct Memory Access (DMA)", "What is Direct Memory Access (DMA) and why is it used?", "A hardware module that transfers blocks of data between I/O devices and RAM directly, bypassing the CPU.", "Saves CPU from handling individual byte interrupt cycles, freeing it for application computation.", ["I/O Devices"], "Common", "Medium"),
        ("Hard vs Soft Real-Time Systems", "Compare Hard and Soft Real-Time systems.", "Hard: Missing a deadline causes system failure (e.g. pacemakers, airbags). Soft: Deadlines are preferred but not catastrophic (e.g. streaming).", "Hard real-time requires deterministic response limits. Soft real-time handles latency averages gracefully.", ["OS Basics"], "Common", "Medium"),
        ("File Allocation Table (FAT)", "How does a FAT file system store files?", "Uses a linked list table where each entry points to the next cluster index of the file on disk.", "Simple to implement but has poor search times for large files as it requires sequential traversal.", ["File Systems"], "Common", "Medium"),
        ("Symlink vs Hard Link", "Compare Symbolic Links (symlink) and Hard Links.", "Hard Link: Direct pointer to the file's inode; deleting original file keeps data. Symlink: Text pointer to original path; breaks if moved.", "Hard links cannot cross file systems or link directories. Symlinks can link directories across storage drives.", ["File Systems"], "Common", "Medium"),
        ("Fork-Join Model", "What is the Fork-Join concurrency model?", "A parallel execution model where a thread splits ('forks') into sub-tasks running in parallel, and waits ('joins') for them to finish.", "Implemented in Java's ForkJoinPool, which uses work-stealing algorithms to maximize CPU core utilization.", ["Concurrency"], "Common", "Medium")
    ]
    
    # 4. HLD (40 unique questions)
    hld_list = [
        ("URL Shortener Design", "How do you design a scalable URL Shortener (TinyURL) system?", "Use Base62 encoding on unique IDs, check duplicates with database index, and cache hot links in Redis.", "Handles millions of daily requests using API Gateways, relational lookup tables, and Memcached/Redis layers.", ["System Design", "HLD"], "Very Common", "Medium"),
        ("Netflix Video Streaming Design", "Design Netflix/YouTube video streaming architecture.", "Upload videos to storage bucket (S3), encode videos into resolutions, and distribute via CDN caching nodes.", "Uses Adaptive Bitrate Streaming (HLS/DASH). Relies on NoSQL database for metadata and user tracking.", ["System Design", "HLD"], "Very Common", "Hard"),
        ("WhatsApp Chat Design", "Design a real-time instant messaging system (WhatsApp).", "Maintain persistent WebSockets or long-polling TCP connections. Route messages via chat service, caching undelivered messages in database.", "Message status (sent/delivered/read) is managed through event streams. Uses Cassandra for message history storage.", ["System Design", "HLD"], "Very Common", "Hard"),
        ("Uber Ride Sharing Design", "Design the Uber ride-sharing matching backend.", "Use geospatial index ring (Uber H3, Google S2) to map riders and drivers. Telemetry coordinates stream via WebSockets/Kafka.", "Match loops scan driver regions within cell indexes, calculating paths and ETAs using routing algorithms.", ["System Design", "HLD"], "Very Common", "Hard"),
        ("Twitter Feed Design", "Design Twitter/Instagram feed and timeline system.", "Use Fan-out on Write (push) for normal users, caching timelines in Redis. Use Fan-out on Read (pull) for celebrity users.", "Hybrid approach avoids write amplification on celebrity tweets while keeping timeline generation fast.", ["System Design", "HLD"], "Very Common", "Hard"),
        ("Rate Limiter Design", "Design an API Rate Limiter.", "Use Token Bucket, Leaking Bucket, or Sliding Window Log algorithms in Redis.", "Rate limiter sits in API Gateway, matching user ip/token to a counter block, returning HTTP 429 if exceeded.", ["System Design", "HLD"], "Very Common", "Medium"),
        ("Distributed Cache Design", "Design a Distributed Cache system (Redis Cluster).", "Use consistent hashing to shard keys across cache servers. Implement primary-replica node pairs for failover.", "Cache eviction utilizes LRU or LFU algorithms. Synchronization writes use gossip protocols for clustering.", ["System Design", "HLD"], "Common", "Hard"),
        ("E-commerce Payment Design", "Design a highly reliable e-commerce payment gateway integration.", "Use idempotent transaction tokens, distributed lock systems, and state machines to manage transaction phases.", "Requires message queues for retry logs, handling third-party webhook callbacks gracefully, and reconciliation loops.", ["System Design", "HLD"], "Very Common", "Hard"),
        ("Web Crawler Design", "Design a distributed Web Crawler.", "Maintain a URL queue, duplicate checker (Bloom filter), HTML Downloader, and Parser.", "Respects robots.txt using domain rate limiting rules. Saves parsed page indexes in distributed store.", ["System Design", "HLD"], "Common", "Hard"),
        ("Notification Engine Design", "Design a Notification Service at scale.", "Use priority queues (RabbitMQ/Kafka) to decouple notification triggers. Scale dispatch workers to send emails/SMS/push.", "Handles template rendering, third-party provider failovers, client opt-outs, and device token registries.", ["System Design", "HLD"], "Very Common", "Medium"),
        ("Ticketmaster Booking Design", "Design Ticketmaster (seat booking system).", "Use transactional databases, caching active seating grids, and distributed locks (Redis) to hold seats during checkout.", "Once checkout timer expires, release locks. Prevents double-booking using database isolation (Repeatable Read).", ["System Design", "HLD"], "Very Common", "Hard"),
        ("Google Docs Design", "Design a collaborative real-time document editor (Google Docs).", "Use Operational Transformation (OT) or Conflict-Free Replicated Data Types (CRDT) to merge text edits.", "Client connections persist via WebSockets. Changes push to document coordinator to resolve synchronization conflicts.", ["System Design", "HLD"], "Common", "Hard"),
        ("Autocomplete System Design", "Design autocomplete typeahead search suggestions.", "Build a Trie (Prefix Tree) structured from query search logs. Cache top search outputs on each prefix node.", "Deploy trie nodes to CDN locations. Debounce user keystrokes on the frontend before calling APIs.", ["System Design", "HLD"], "Very Common", "Medium"),
        ("Kafka Broker Design", "Design a Distributed Message Queue (Kafka-like).", "Store message offsets sequentially in partition log files on disk. Consumers pull data from offset points.", "Scale read-write throughput using sharded partitions. Uses zero-copy OS transfers to speed up read sockets.", ["System Design", "HLD"], "Common", "Hard"),
        ("Distributed Key-Value Store", "Design a partitioned, replicated key-value storage engine (DynamoDB-like).", "Use Consistent Hashing for sharding, Raft/Paxos consensus for replication, and LSM Trees for writes.", "Supports tunable consistency (R + W > N) for read/write nodes, and uses vector clocks to resolve data conflicts.", ["System Design", "HLD"], "Common", "Hard"),
        ("CDN Architecture", "Design a Content Delivery Network (CDN).", "Deploy proxy caching nodes at edge server locations. Use Geo-DNS routing to direct users to the closest node.", "Edge nodes cache static assets (images, js) and use cache invalidation protocols (TTL, purge APIs) to update contents.", ["System Design", "HLD"], "Common", "Medium"),
        ("Monitoring Alerting Design", "Design a metric monitoring and alerting system.", "Use time-series databases (InfluxDB) for metric aggregation. Pull logs using daemon agents (Prometheus format).", "Rules engine runs cron sweeps over databases, pushing alerts to notification channels if metrics exceed thresholds.", ["System Design", "HLD"], "Common", "Hard"),
        ("Distributed File System", "Design a Distributed File System (GFS/HDFS-like).", "A Master node tracks directory metadata and maps files to chunk locations. Chunkservers store data blocks.", "Files are split into fixed blocks (64MB) and replicated across multiple rack servers for durability.", ["System Design", "HLD"], "Common", "Hard"),
        ("Leaderboard Design", "Design a real-time gaming leaderboard system.", "Use Redis Sorted Sets (ZSET) to store user scores. Retrieve user ranks using logarithmic operations.", "Distribute read queries via read replicas. Scales write loads using batch updates.", ["System Design", "HLD"], "Common", "Medium"),
        ("Yelp NearBy Places Design", "Design Yelp / Google Maps proximity service.", "Use Quadtrees or Geohashes to index latitude/longitude coordinates into localized square grids.", "Queries compute the geohash of search coordinates and query databases to fetch places sharing matching prefixes.", ["System Design", "HLD"], "Common", "Hard"),
        ("API Gateway Design", "Design a scalable API Gateway.", "Gateway acts as single entrypoint handling routing, SSL termination, authentication, rate limiting, and request telemetry.", "Deploy gateway clusters behind network load balancers (Layer 4). Build gateway logic using non-blocking I/O.", ["System Design", "HLD"], "Common", "Medium"),
        ("Search Engine Design", "Design a search engine indexer.", "Use inverted index structures mapping keywords to doc IDs (ElasticSearch). Crawl web pages, clean text, and score using TF-IDF.", "Scale searches using partitioned shards. Cache search terms at boundary caches.", ["System Design", "HLD"], "Common", "Hard"),
        ("Zoom Backend Design", "Design a Zoom-like video conferencing system.", "Use WebRTC for peer-to-peer streams. For group calls, route media streams through Selective Forwarding Units (SFUs).", "SFUs dynamically adjust bandwidth feeds, sending compressed streams matching client connection capacities.", ["System Design", "HLD"], "Common", "Hard"),
        ("Ad Click Ingestion", "Design a high-throughput ad-click aggregator.", "Ingest clicks via Kafka queues. Stream processing engines (Flink/Spark) aggregate clicks per minute in time windows.", "Saves aggregated data to Cassandra or Elasticsearch for analytical dashboard querying.", ["System Design", "HLD"], "Common", "Hard"),
        ("Dropbox Storage Design", "Design a cloud storage system (Dropbox/OneDrive).", "Upload chunks of files to S3 block storage. Keep file metadata and history states in relational database.", "Sync service notifies clients of edits using long-polling or WebSockets. Minimizes bandwidth using delta sync.", ["System Design", "HLD"], "Common", "Hard"),
        ("DNS Architecture Design", "Design a highly available Domain Name System (DNS).", "DNS uses hierarchical caching (Browser, Router, ISP, Recursive, TLD, Root, Authoritative servers).", "Queries resolve IP addresses via UDP packets, caching records locally with appropriate TTL headers.", ["System Design", "HLD"], "Common", "Medium"),
        ("Online Bookstore Design", "Design an online bookstore (Amazon).", "Decouple services: Catalog, Cart, Order, Payment. Scale catalog read operations using search index caching.", "Inventory checks use optimistic locking. Async worker loops process payments, email receipts, and update stock.", ["System Design", "HLD"], "Common", "Medium"),
        ("Snowflake ID Generator", "Design a distributed unique ID generator (Twitter Snowflake).", "Generate 64-bit IDs using: 1-bit unused, 41-bit timestamp, 10-bit worker ID, and 12-bit sequence counter.", "Allows coordinate-free local generation of sorted IDs without database network roundtrips.", ["System Design", "HLD"], "Common", "Medium"),
        ("WebSocket Server Scale", "How do you scale WebSocket connections to 1 million active clients?", "Deploy WebSocket servers behind Layer 7 load balancers supporting session affinity (sticky sessions).", "Optimize server OS limits (sysctl file descriptors), and use a Redis pub-sub backplane to broadcast messages.", ["System Design", "HLD"], "Common", "Hard"),
        ("Flash Sale System Design", "Design a flash sale inventory reservation system.", "Store inventory counts in Redis. Process allocations using Lua scripts to guarantee atomicity.", "Queue successful checkout requests to database sequentially. Keeps database protected from spike loads.", ["System Design", "HLD"], "Very Common", "Hard"),
        ("Live Streaming Twitch Design", "Design a live streaming video server (Twitch).", "Ingest RTMP stream from broadcaster. Transcode stream into multiple quality levels (ABR) using worker machines.", "Distribute live video segments using HLS protocols through CDN edge nodes.", ["System Design", "HLD"], "Common", "Hard"),
        ("E-Commerce Cart Design", "Design a highly available shopping cart service.", "Use DynamoDB or Redis to persist cart records. Allow guest carts to store data in local cookies.", "Merge guest carts with user databases during login. Optimizes database queries using batch updates.", ["System Design", "HLD"], "Common", "Medium"),
        ("Logistics Tracking Design", "Design a logistics parcel tracking system.", "Ingest location pings to Kafka. Store coordinate history in time-series databases or NoSQL wide-column stores.", "Cache current parcel location in Redis for quick dashboard updates.", ["System Design", "HLD"], "Common", "Medium"),
        ("Ride Match loop Design", "Design matching loops for ride-booking systems.", "Scan active driver coordinates in client Geohash partitions. Queue requests to a ride matcher engine.", "Uses worker threads to check drivers sequentially, notifying selected driver via WebSocket. Expire requests if timeout.", ["System Design", "HLD"], "Common", "Hard"),
        ("Distributed Cron Design", "Design a distributed cron job scheduler.", "Store job triggers in a relational database with execution states. Use distributed locks to prevent duplicate execution.", "Workers fetch jobs whose triggers are in range, execute them, and update status back to database.", ["System Design", "HLD"], "Common", "Hard"),
        ("Geo-Fencing Alert System", "Design a geo-fencing advertising system.", "Track user coordinates. Match coordinates to geo-fence boundaries (polygons) cached in spatial databases.", "Send push notification triggers if coordinate intersects user's target perimeter.", ["System Design", "HLD"], "Common", "Hard"),
        ("Collaborative Whiteboard", "Design a real-time collaborative drawing canvas.", "Broadcast vector drawing paths (lines, circles) as coordinate events via WebSockets to connected channel peers.", "Replay history events to new users connecting. Save canvas state as image chunks on S3.", ["System Design", "HLD"], "Common", "Medium"),
        ("Analytics Dashboard Design", "Design a real-time analytics dashboard system.", "Ad-click telemetry flows to Kafka, aggregated by Spark Streaming. Saves data to time-series database.", "Frontend polls API or opens Server-Sent Events (SSE) connections to fetch aggregated graph statistics.", ["System Design", "HLD"], "Common", "Hard"),
        ("Distributed Lock Manager", "Design a Distributed Lock Service (ZooKeeper-like).", "Implement consensus protocols (Paxos) across nodes. Provide heartbeats to maintain lease ownership of lock paths.", "Clients acquire locks by creating ephemeral sequential nodes. If master fails, backups elect a new leader.", ["System Design", "HLD"], "Common", "Hard"),
        ("Fraud Detection Design", "Design a real-time card fraud detection engine.", "Ingest payment events. Run event through rule engines and ML model inference engines (e.g. check limits, location).", "Must evaluate transaction validity within 100ms. Aborts transaction if fraud threshold is exceeded.", ["System Design", "HLD"], "Common", "Hard")
    ]
    
    # 5. LLD (40 unique questions)
    lld_list = [
        ("Parking Lot Design", "Design a Parking Lot system using Object-Oriented Principles.", "Define classes: ParkingLot, Floor, ParkingSpot (Compact, Large), Vehicle (Car, Bike), Ticket, Payment.", "Use Strategy pattern for dynamic parking assignment. Enforce thread-safe booking of parking spots.", ["System Design", "LLD"], "Very Common", "Medium"),
        ("Movie Booking Design", "Design BookMyShow LLD.", "Define classes: Cinema, Hall, Movie, Show, Seat (Gold, Silver), Booking, Payment, User.", "Manage seat reservation concurrency using state pattern and lock timeouts. Use singleton for booking processor.", ["System Design", "LLD"], "Very Common", "Medium"),
        ("Splitwise Design", "Design Splitwise expense sharing app.", "Define classes: User, Expense (Equal, Exact, Percent), Split, Group, ExpenseManager.", "Implement transaction simplification algorithm using graphs to minimize total transaction count.", ["System Design", "LLD"], "Very Common", "Medium"),
        ("Chess Game Design", "Design a Chess Game LLD.", "Define classes: Board, Cell, Piece (King, Queen, Rook, Bishop, Knight, Pawn), Move, Game, Player.", "Represent pieces using inheritance. Implement move validation rules inside each piece class.", ["System Design", "LLD"], "Common", "Medium"),
        ("Elevator System Design", "Design an Elevator System LLD.", "Define classes: ElevatorController, Car, Button (Internal, External), DispatchStrategy, Door.", "Use Strategy pattern to handle elevator selection algorithms (e.g. SCAN). Use state pattern to track car directions.", ["System Design", "LLD"], "Very Common", "Medium"),
        ("Vending Machine Design", "Design a Vending Machine LLD.", "Define classes: VendingMachine, State (Idle, HasMoney, Dispensing, OutOfStock), Inventory, Product, Coin.", "Use State design pattern to manage Vending Machine operations and transitions cleanly.", ["System Design", "LLD"], "Very Common", "Medium"),
        ("Library Management Design", "Design a Library Management System.", "Classes: Library, Book, BookItem, Account (Librarian, Member), BookLending, Reservation.", "Implement fine calculation strategies and search indexes for books based on title, author, and subject.", ["System Design", "LLD"], "Common", "Medium"),
        ("ATM Design", "Design an ATM Machine LLD.", "Classes: ATM, ATMState (Idle, CardInserted, PinEntered, CashDispensed), Card, Account, CashDispenser.", "Use Chain of Responsibility pattern for cash dispensing ($100, $500, $2000 bills). Use State pattern for ATM flow.", ["System Design", "LLD"], "Very Common", "Medium"),
        ("Hotel Management Design", "Design a Hotel Management System.", "Classes: Hotel, Room (Suite, Deluxe), Guest, Booking, Invoice, Receptionist.", "Manage room booking status and dynamic pricing strategies based on season and room occupancy.", ["System Design", "LLD"], "Common", "Medium"),
        ("Cricinfo Design", "Design Cricinfo scoreboard LLD.", "Classes: Match, Innings, Team, Player, Ball, Run, Over, Scoreboard.", "Use Observer design pattern to broadcast ball-by-ball score updates to multiple display dashboards.", ["System Design", "LLD"], "Common", "Medium"),
        ("Online Shopping Design", "Design an online shopping cart system (Amazon LLD).", "Classes: Catalog, Product, Item, Order, Shipment, ShoppingCart, Payment.", "Use Strategy pattern for checkout payments. Use State pattern to track order shipping phases.", ["System Design", "LLD"], "Common", "Medium"),
        ("Meeting Scheduler Design", "Design a Meeting Room Scheduler.", "Classes: Scheduler, MeetingRoom, Meeting, User, Calendar.", "Provide functions to search available rooms in a time slot. Handle meeting invitation notifications.", ["System Design", "LLD"], "Common", "Medium"),
        ("Snakes & Ladders Design", "Design Snakes and Ladders game.", "Classes: Board, Cell (Snake, Ladder, Empty), Player, Die, Game.", "Represent board grid recursively. Implement game loops in the Game controller.", ["System Design", "LLD"], "Common", "Medium"),
        ("Blackjack LLD Design", "Design Blackjack card game LLD.", "Classes: Deck, Card, Hand, Player, Dealer, Game.", "Provide deck shuffling logic. Implement scoring checks and dealer play rules.", ["System Design", "LLD"], "Common", "Medium"),
        ("BookMyShow Seat Allocator", "How do you design a thread-safe seat allocation engine in BookMyShow?", "Use optimistic locking on Seat rows or acquire a localized Redis lock on the Show ID during booking.", "Locks prevent double-booking. Set a 5-minute timeout state on reserved seats, releasing them if checkout fails.", ["Concurrency", "LLD"], "Common", "Hard"),
        ("Cache Framework Design", "Design an in-memory Cache Framework LLD.", "Classes: Cache, Storage (HashMap), EvictionPolicy (LRU, LFU).", "Use Strategy pattern for eviction. LRU uses a Doubly Linked List alongside HashMap. Make all operations thread-safe.", ["System Design", "LLD"], "Common", "Medium"),
        ("Logger Library Design", "Design a Logger Library.", "Classes: Logger, LogLevel (INFO, DEBUG, ERROR), LogPublisher (Console, File).", "Use Chain of Responsibility to pass logs through level checks. Use Adapter pattern for publishers.", ["System Design", "LLD"], "Common", "Medium"),
        ("Trello Task Planner", "Design a Trello/Jira Task Planner LLD.", "Classes: Board, List, Task, Member, ActivityLog.", "Implement sorting of tasks. Provide search and assignment filters. Track modification logs.", ["System Design", "LLD"], "Common", "Medium"),
        ("File Directory LLD", "Design a file system directory structure LLD.", "Classes: File, Directory, Inode. Use Composite design pattern.", "Treat both files and directories as components of a unified file system, allowing recursive size calculations.", ["System Design", "LLD"], "Common", "Medium"),
        ("Rate Limiter Class Design", "Design LLD class structure of a Rate Limiter.", "Classes: RateLimiter, TokenBucket, UserBucketRegistry. Use Singleton pattern for registry.", "Implement token bucket calculation class checking if token availability exceeds user consumption rate limit.", ["System Design", "LLD"], "Common", "Medium"),
        ("Pizza Customizer Design", "Design a Pizza customization builder.", "Classes: Pizza, ToppingDecorator (Cheese, Olives, Tomato). Use Decorator pattern.", "Wrap base pizza object with topping decorator objects to calculate dynamic prices and descriptions.", ["System Design", "LLD"], "Common", "Easy"),
        ("Digital Wallet Design", "Design a Digital Wallet system (Paytm LLD).", "Classes: Wallet, User, Account, Transaction, PaymentProcessor.", "Handle concurrent wallet balance transfers using synchronized blocks or database row-level locking.", ["System Design", "LLD"], "Common", "Medium"),
        ("Food Delivery LLD", "Design a food delivery system (Zomato/Swiggy LLD).", "Classes: Zomato, Restaurant, MenuItem, Order, DeliveryRider, Cart.", "Use Observer pattern to notify riders of new orders. Use Strategy pattern to assign drivers.", ["System Design", "LLD"], "Common", "Medium"),
        ("Uber LLD Class Design", "Design a ride-booking system LLD.", "Classes: Uber, Customer, Driver, Cab, Trip, Payment.", "Implement driver location updates. Calculate trip price using Strategy pattern (e.g. SurgePricing).", ["System Design", "LLD"], "Common", "Medium"),
        ("Document Editor Undo", "Design a document editor supporting Undo/Redo commands.", "Classes: Editor, Document, Command (InsertText, DeleteText), CommandHistory. Use Command pattern.", "Store executed command objects in a history stack, popping them to call undo() on user request.", ["System Design", "LLD"], "Common", "Medium"),
        ("Social Connections LLD", "Design a social network connections manager.", "Classes: UserManager, User, ConnectionRequest, Message.", "Use Graph algorithms to find degrees of separation between users (BFS for shortest path).", ["System Design", "LLD"], "Common", "Medium"),
        ("Airline Reservation LLD", "Design an Airline Reservation system LLD.", "Classes: Flight, Airport, Route, Aircraft, Passenger, Booking.", "Manage seat maps, flight status changes, and user ticket allocations.", ["System Design", "LLD"], "Common", "Medium"),
        ("Online Auction System", "Design an online auction/bidding platform.", "Classes: Auction, Item, Bid, Bidder. Use Observer design pattern.", "Notify all active bidders when a new highest bid is placed on an item. Manage auction state transitions.", ["System Design", "LLD"], "Common", "Medium"),
        ("StackOverflow LLD", "Design Stack Overflow Q&A system LLD.", "Classes: Question, Answer, Comment, Tag, User, Vote (Up/Down), Reputation.", "Track user reputation scores based on votes. Implement search filters on tags and content.", ["System Design", "LLD"], "Common", "Medium"),
        ("Message Queue Classes", "Design class structure of an in-memory Message Queue.", "Classes: MessageQueue, Topic, Partition, Producer, Consumer, ConsumerGroup.", "Manage thread-safe message publishing to partitions. Route messages to consumer group members.", ["System Design", "LLD"], "Common", "Hard"),
        ("Cab Match LLD", "Design cab matching strategies class structure.", "Classes: CabFinder, MatchingStrategy (NearestDriver, BestRatedDriver), LocationService.", "Use Strategy pattern to switch matching algorithms dynamically based on user preferences.", ["System Design", "LLD"], "Common", "Medium"),
        ("Shopping Cart Promos", "Design discount codes and promo configurations for shopping carts.", "Classes: CartItem, DiscountDecorator (CouponDiscount, FreeShippingDecorator). Use Decorator pattern.", "Apply multiple overlapping discount rules to base cart calculations sequentially.", ["System Design", "LLD"], "Common", "Medium"),
        ("Notification Observer", "Design a notification broadcaster.", "Classes: NotificationManager, Subscriber (EmailSubscriber, SMSSubscriber), Message. Use Observer pattern.", "Broadcast message updates to all registered channels when matching event triggers occur.", ["System Design", "LLD"], "Common", "Easy"),
        ("Auth RBAC LLD", "Design Role-Based Access Control (RBAC) class structure.", "Classes: AuthManager, User, Role, Permission. Use Singleton pattern for AuthManager.", "Validate if user has required permissions assigned to their roles before granting resource access.", ["System Design", "LLD"], "Common", "Medium"),
        ("Thread Pool LLD", "Design a custom Thread Pool class structure.", "Classes: ThreadPool, WorkerThread, TaskQueue. Make queue access synchronized.", "Worker threads loop, checking TaskQueue for jobs, executing them, and returning to idle state.", ["Concurrency", "LLD"], "Common", "Hard"),
        ("Key-Value Store Classes", "Design classes of an in-memory transactional Key-Value Store.", "Classes: KeyValueStore, Transaction, CommandStack. Support nested transaction rollback.", "Store commands in a stack during a transaction, applying changes to master map on commit, or discarding on rollback.", ["System Design", "LLD"], "Common", "Hard"),
        ("Car Rental LLD", "Design a Car Rental system LLD.", "Classes: RentalSystem, Store, Vehicle (Car, SUV, Bike), Reservation, Bill, Payment.", "Manage vehicle inventory, reservations, pickup/drop times, and billing calculations.", ["System Design", "LLD"], "Common", "Medium"),
        ("Ticket Resolution LLD", "Design a customer ticket resolution workflow.", "Classes: TicketManager, Ticket, Agent, Category, EscalationStrategy. Use State pattern.", "Manage ticket states (Open, Assigned, Resolved, Closed). Escalate tickets if unresolved within SLAs.", ["System Design", "LLD"], "Common", "Medium"),
        ("E-Commerce Order State", "Design e-commerce order state machine LLD.", "Classes: Order, OrderState (Created, Paid, Shipped, Delivered, Cancelled). Use State pattern.", "Define valid transition checks inside each state class, preventing out-of-order state updates.", ["System Design", "LLD"], "Common", "Medium"),
        ("Distributed Lock LLD", "Design classes for a distributed lock implementation client.", "Classes: LockClient, LockRegistry, LeaseTimer.", "Manage heartbeats to maintain lock lease validity, and handle automatic lock release on network split.", ["Concurrency", "LLD"], "Common", "Hard")
    ]
    
    # 4. Java (50 unique questions)
    java_list = [
        ("JVM Memory Structure", "Explain the memory structure of Java Virtual Machine (JVM).", "JVM memory is divided into Heap, Stack, Method Area (Metaspace), PC Registers, and Native Method Stacks.", "Heap stores objects (shared). Stack stores local variables and frame blocks (thread-isolated). Metaspace stores class metadata.", ["Java", "JVM"], "Very Common", "Medium"),
        ("Garbage Collection", "How does Garbage Collection work in Java and compare G1GC and ZGC.", "GC reclaims heap memory by destroying unreachable objects. Generational GC categorizes objects into Young and Old.", "G1GC is regional, balancing pause times and throughput. ZGC is concurrent, keeping pauses under 10ms at scale.", ["Java", "Garbage Collection"], "Very Common", "Medium"),
        ("HashMap Internals", "Explain the internal working of HashMap and collision resolution.", "HashMap uses an array of buckets. Keys map to index via hash code. Collisions resolve via linked list, treeified above limit.", "Java 8 treeifies buckets containing >= 8 items into Red-Black Trees, reducing lookup from O(N) to O(log N).", ["Java", "Collections"], "Very Common", "Medium"),
        ("Java Memory Model", "What is the volatile keyword and how does it relate to Java Memory Model?", "volatile guarantees thread visibility and prevents instruction reordering. Writes write to main memory directly.", "Prevents threads from caching local variables in CPU registers, enforcing visibility changes across cores.", ["Java", "Multithreading"], "Very Common", "Medium"),
        ("Interface vs Abstract Class", "Compare Abstract Classes and Interfaces in Java 8+.", "Abstract class allows state and constructors. Interface defines behavior contracts. Java 8+ allows default and static methods.", "Java 9 added private methods to interfaces. Multiple inheritance is only possible through interfaces.", ["Java", "OOP"], "Common", "Easy"),
        ("Java Streams API", "Explain Stream API and functional interface lambda expressions.", "Stream API provides functional processing pipelines over collections. Lambda expressions implement functional interfaces.", "Streams execute lazily using intermediate operations (filter, map) and terminal operations (collect, reduce).", ["Java", "Streams"], "Common", "Medium"),
        ("Java Multithreading", "Explain Executor Framework and CompletableFuture in Java.", "Executor Framework manages thread pools. CompletableFuture enables non-blocking async programming via callback pipelines.", "CompletableFuture supports thenApply, thenCompose, and exceptionally methods for asynchronous workflows.", ["Java", "Concurrency"], "Very Common", "Medium"),
        ("Serialization", "What is Serialization and explain the transient keyword.", "Serialization converts object state into binary byte streams. transient prevents fields from being serialized.", "Classes must implement Serializable. transient is used for sensitive data (passwords) or temporary caches.", ["Java", "Serialization"], "Common", "Medium"),
        ("Reflection API", "What is Java Reflection and its drawbacks?", "Allows examining and modifying runtime behaviors of classes, fields, and methods at runtime.", "Drawbacks: Bypasses access modifiers (private), incurs performance overhead, and breaks compile-time type safety.", ["Java", "Reflection"], "Common", "Medium"),
        ("ClassLoaders", "Explain ClassLoaders in Java.", "Dynamic subsystems loading class files into Metaspace. Uses Delegation Hierarchy model: Bootstrap -> Extension -> Application.", "Classes load on-demand. Custom class loaders can load files from remote servers or databases.", ["Java", "JVM"], "Common", "Hard"),
        ("Checked vs Unchecked", "What is the difference between Checked and Unchecked Exceptions?", "Checked: Verified at compile-time (inherits Exception). Unchecked: Verified at runtime (inherits RuntimeException).", "Checked exceptions require try-catch or throws clauses. Unchecked exceptions denote programming errors (NullPointer).", ["Java", "Exceptions"], "Common", "Easy"),
        ("String Constant Pool", "Explain String Constant Pool and Immutability of Strings.", "String Constant Pool is a special heap area storing literal strings to optimize memory.", "Strings are immutable to prevent security issues, handle thread-safety, and allow pool caching.", ["Java", "Strings"], "Very Common", "Easy"),
        ("Equals and HashCode", "What is the contract between equals() and hashCode()?", "If two objects are equal according to equals(), their hashCode() values must be identical.", "If objects have same hashCode(), they are not necessarily equal. Violating this contract breaks HashMaps.", ["Java"], "Very Common", "Easy"),
        ("Fail-Fast vs Fail-Safe", "Compare Fail-Fast and Fail-Safe iterators.", "Fail-Fast throws ConcurrentModificationException if collection changes during iteration. Fail-Safe iterates over a copy.", "ArrayList iterator is Fail-Fast. CopyOnWriteArrayList iterator is Fail-Safe, avoiding modifications block.", ["Java", "Collections"], "Common", "Medium"),
        ("ConcurrentHashMap", "How does ConcurrentHashMap achieve high concurrency?", "ConcurrentHashMap uses bucket lock segments (reentrant locks on node heads) instead of locking the entire map.", "Multiple threads can write to different buckets concurrently. Read operations are lock-free using volatile nodes.", ["Java", "Collections"], "Very Common", "Hard"),
        ("ThreadLocal", "What is ThreadLocal and when does it cause memory leaks?", "Provides thread-isolated variables. Each thread holds a local copy inside a ThreadLocalMap.", "Memory leaks occur if thread pools reuse threads without calling remove(), leaving references in dead threads.", ["Java", "Concurrency"], "Common", "Hard"),
        ("Type Erasure", "What is Type Erasure in Java Generics?", "Compiler replaces generic types with Object or upper bounds, adding casts and deleting generic details at compile time.", "Enforces backwards compatibility. Type details are unavailable at runtime via reflection.", ["Java"], "Common", "Medium"),
        ("Try With Resources", "How does Try-With-Resources manage database connections?", "Automatically closes resources at transaction end. Target class must implement AutoCloseable interface.", "Replaces verbose finally blocks, ensuring connections close even if exceptions trigger.", ["Java", "Exceptions"], "Common", "Easy"),
        ("JVM Options Tuning", "Explain JVM tuning parameters: -Xms, -Xmx, and garbage collector configuration.", "-Xms: Sets initial heap size. -Xmx: Sets max heap size. -XX:+UseG1GC: Enables G1 Garbage Collector.", "Tuning heap sizes avoids OutOfMemory errors and GC pauses by sizing memory allocations to app loads.", ["Java", "JVM"], "Common", "Medium"),
        ("Marker Interfaces", "What are Marker Interfaces in Java?", "Interfaces with no declared methods, used to deliver metadata capabilities to the compiler or JVM.", "Examples: Cloneable (allows clone()), Serializable (allows serialization), and Remote.", ["Java"], "Common", "Easy"),
        ("Thread States", "What are the different Thread States in Java?", "NEW, RUNNABLE, BLOCKED, WAITING, TIMED_WAITING, and TERMINATED.", "Blocked: Waiting for a monitor lock. Waiting: Waiting indefinitely for another thread's signal (join/wait).", ["Java", "Concurrency"], "Common", "Medium"),
        ("Object Class Methods", "Explain wait(), notify(), and notifyAll() contract.", "wait() releases lock and sleeps thread. notify() wakes up one waiting thread. notifyAll() wakes all.", "Must be called from a synchronized context (owning the object monitor), otherwise throws IllegalMonitorStateException.", ["Java", "Concurrency"], "Common", "Medium"),
        ("Deep vs Shallow Copy", "Compare Deep Copy and Shallow Copy.", "Shallow copy copies primitive fields; reference fields point to the original objects. Deep copy duplicates nested objects recursively.", "Shallow copy shares references, risking side effects. Deep copy creates isolated duplicates.", ["Java"], "Common", "Easy"),
        ("Immutable Class Rules", "How do you create an Immutable Class in Java?", "Declare class final, declare all fields private and final, provide no setters, and return deep copies of mutable fields.", "Prevents state modifications after initialization, ensuring absolute thread-safety.", ["Java"], "Common", "Medium"),
        ("Synchronized vs ReentrantLock", "Compare synchronized blocks and ReentrantLock.", "synchronized is implicit, locked to monitor blocks. ReentrantLock is explicit, supporting timeouts and fair locks.", "ReentrantLock allows tryLock() (non-blocking lock attempt) and lockInterruptibly() for fine-grained control.", ["Java", "Concurrency"], "Common", "Medium"),
        ("Java Deadlocks", "How do you debug Java thread deadlocks?", "Use jstack utility or thread dumps to scan thread states. Detects circles of blocked threads holding locks.", "VisualVM or JConsole provide graphical interfaces to trace deadlock stack lines.", ["Java", "Concurrency"], "Common", "Medium"),
        ("Java Memory Leaks", "What causes memory leaks in Java if it has a Garbage Collector?", "Unintentional retention of object references in static fields, thread pools, or unclosed resource streams.", "Garbage Collector cannot reclaim objects if they are reachable from active root references.", ["Java", "JVM"], "Common", "Medium"),
        ("System gc", "Does calling System.gc() guarantee immediate garbage collection?", "No. System.gc() only suggests to the JVM that it should run GC; the JVM decides when and if to execute it.", "Calling it manually should be avoided as it triggers stop-the-world full GC sweeps, degrading performance.", ["Java", "Garbage Collection"], "Common", "Easy"),
        ("Functional Interfaces", "Explain Predicate, Consumer, and Function interfaces.", "Predicate: Accepts one input, returns boolean. Consumer: Accepts input, returns void. Function: Accepts input, returns output.", "Used heavily in Stream map, filter, and forEach pipelines to write declarative, functional code.", ["Java", "Streams"], "Common", "Medium"),
        ("Optional Class", "Why was the Optional class introduced in Java 8?", "To provide a type-level wrapper representing optional values, helping developers avoid NullPointerExceptions.", "Encourages writing declarative checks like map(), filter(), or orElseThrow() instead of nested null blocks.", ["Java"], "Common", "Easy"),
        ("Reference Types", "Explain WeakReference, SoftReference, and PhantomReference.", "Weak: GC reclaims immediately. Soft: GC reclaims only when memory is low. Phantom: GC queue references for post-mortem cleanup.", "SoftReferences are optimal for caching. WeakReferences are used in WeakHashMap to avoid leaks.", ["Java", "JVM"], "Common", "Hard"),
        ("Double Brace Initialization", "Why is Double Brace Initialization considered an anti-pattern?", "Creates an anonymous inner class holding a hidden reference to the enclosing outer instance.", "Enclosing reference prevents the outer instance from being garbage collected, causing memory leaks.", ["Java"], "Common", "Medium"),
        ("Java 9 Modules", "What is the purpose of the Java 9 Module System (Project Jigsaw)?", "Provides modular packaging (module-info.java) to encapsulate packages, reducing runtime sizes and improving security.", "Enforces strict encapsulation, allowing classes to export only specified APIs to other modules.", ["Java"], "Common", "Hard"),
        ("Project Loom Virtual Threads", "What are Virtual Threads (Project Loom) in Java 21?", "Lightweight user-mode threads managed by JVM runtime instead of OS. Spawning millions of virtual threads is cheap.", "Eliminates thread-per-request OS bottlenecks, improving scalability of synchronous blocking I/O apps.", ["Java", "Concurrency"], "Very Common", "Hard"),
        ("Records in Java", "What are Records in Java?", "Shallowly immutable data carrier classes introduced in Java 16. Automatically generates constructor, equals, hashCode, and toString.", "Reduces boilerplate code for DTOs. Fields are private and final, accessed via reader methods matching field names.", ["Java"], "Common", "Easy"),
        ("Pattern Matching switch", "Explain Pattern Matching for switch in Java 21.", "Allows switch expressions to check types of objects, extracting variables inside case conditions directly.", "Reduces verbose instanceof checks and type casts, supporting clean polymorphic routing.", ["Java"], "Common", "Medium"),
        ("Singleton Double Checked Lock", "Explain thread-safe Singleton using Double-Checked Locking.", "Uses synchronized block with a double null check, and declares the instance variable volatile.", "volatile ensures thread visibility and prevents reordering. Double check avoids synchronization overhead once initialized.", ["Java", "Design Patterns"], "Common", "Medium"),
        ("ForkJoinPool work stealing", "How does ForkJoinPool's work-stealing algorithm operate?", "Idle worker threads steal tasks from the back of busy worker threads' double-ended queues (deques).", "Optimizes CPU utilization by keeping all threads busy with subtasks created in parallel fork processes.", ["Java", "Concurrency"], "Common", "Hard"),
        ("BlockingQueue types", "Compare ArrayBlockingQueue and LinkedBlockingQueue.", "ArrayBlockingQueue: Bounded, backed by array, single lock for put/take. LinkedBlockingQueue: Bounded/unbounded, backed by nodes, two locks.", "LinkedBlockingQueue has higher throughput as read and write threads can operate concurrently on separate locks.", ["Java", "Concurrency"], "Common", "Hard"),
        ("CyclicBarrier vs CountDownLatch", "Compare CyclicBarrier and CountDownLatch in Java.", "CountDownLatch: One-time gate; threads wait until count hits zero. CyclicBarrier: Reusable barrier; threads block until all arrive.", "CountDownLatch count cannot be reset. CyclicBarrier can be reset and reused, and allows executing a barrier action.", ["Java", "Concurrency"], "Common", "Medium"),
        ("CopyOnWriteArrayList", "When do you use CopyOnWriteArrayList?", "Use for collections with frequent reads and very rare writes. Creates a fresh copy of the array on every write.", "Mutating operations are expensive, but reads are completely lock-free, avoiding ConcurrentModificationException.", ["Java", "Collections"], "Common", "Medium"),
        ("Object Headers memory", "What is the memory overhead of Object Headers in JVM?", "A Java object header contains a Mark Word (64-bit) for locking/GC, and a Klass Word (64-bit) pointing to metadata.", "In 64-bit architectures, this adds a baseline 12 to 16 bytes memory overhead to every object instance.", ["Java", "JVM"], "Common", "Hard"),
        ("CompletableFuture async", "What is the difference between runAsync and supplyAsync in CompletableFuture?", "runAsync: Accepts a Runnable, returns CompletableFuture<Void>. supplyAsync: Accepts a Supplier, returns CompletableFuture<T>.", "Use supplyAsync when you need to return values from async executions. Both execute in ForkJoinPool by default.", ["Java", "Concurrency"], "Common", "Medium"),
        ("Phaser vs CyclicBarrier", "Compare Phaser and CyclicBarrier.", "Phaser: Flexible synchronization barrier supporting dynamic participant counts. CyclicBarrier: Fixed participant limit.", "Phaser supports multiple phases, and threads can register or deregister dynamically during runtime.", ["Java", "Concurrency"], "Common", "Hard"),
        ("Covariant Returns", "What are Covariant Return Types in Java?", "Allows a subclass overriding method to return a more specific subclass type than the type declared in parent method.", "Eliminates redundant type casts, letting developers work with concrete subclass instances cleanly.", ["Java"], "Common", "Easy"),
        ("ClassNotFound vs NoClassDef", "Compare ClassNotFoundException and NoClassDefFoundError.", "ClassNotFoundException: Checked exception; triggered when Class.forName() fails to load file. NoClassDef: Runtime error; class was present at compile but missing at run.", "NoClassDefFoundError usually indicates configuration issues, classpath changes, or library compilation mismatch.", ["Java", "JVM"], "Common", "Medium"),
        ("Strictfp", "What is the strictfp keyword?", "Ensures floating-point calculations yield identical binary outputs across all platforms and CPU hardware.", "Restricts float/double math to match IEEE 754 standards strictly, avoiding rounding differences on platform architectures.", ["Java"], "Common", "Easy"),
        ("Thread Interruption", "How does Java's thread interruption mechanism work?", "Calling interrupt() sets a boolean flag in target thread. Thread must poll this flag or handle InterruptedException.", "Blocking methods (sleep, wait) throw InterruptedException and clear the flag when interrupted.", ["Java", "Concurrency"], "Common", "Medium"),
        ("Custom Class Loader", "Why would you implement a custom ClassLoader?", "To load classes from custom locations (database, network URL), decrypt class files on the fly, or support hot redeployment.", "Overrides findClass() to read bytecode bytes, and calls defineClass() to register it in JVM.", ["Java", "JVM"], "Common", "Hard"),
        ("Native Memory Tracking", "What is Native Memory Tracking (NMT) in JVM?", "A diagnostic tool to monitor JVM's internal memory allocations (metaspace, thread stacks, GC structures).", "Enabled via JVM flag -XX:NativeMemoryTracking=summary. Traced using jcmd command line tools.", ["Java", "JVM"], "Common", "Hard")
    ]
    
    # 5. Spring Boot (40 unique questions)
    spring_list = [
        ("Dependency Injection", "Explain Dependency Injection (DI) and Inversion of Control (IoC).", "IoC: Delegating object instantiation and lifecycle management to the container. DI: Supplying dependencies to classes at runtime.", "Reduces coupling, simplifies unit testing (mocking dependencies), and automates configuration sweeps.", ["Spring Boot", "Core"], "Very Common", "Medium"),
        ("Bean Scopes", "What are the Bean Scopes in Spring Framework?", "Singleton (default), Prototype, Request, Session, Application, and WebSocket.", "Singleton creates one instance per container. Prototype creates a new instance every time it is requested.", ["Spring Boot", "Core"], "Very Common", "Medium"),
        ("Spring MVC Request Flow", "Describe the request lifecycle in Spring MVC.", "DispatcherServlet intercepts request, queries HandlerMapping, routes to Controller, returns ModelAndView, resolved by ViewResolver.", "In REST APIs, HandlerAdapter executes controller directly, writing JSON bytes to response body via HttpMessageConverter.", ["Spring Boot", "MVC"], "Very Common", "Medium"),
        ("Spring Boot AutoConfiguration", "Explain Spring Boot Auto-Configuration mechanism.", "Scans classpath for starter libraries. Automatically configures beans matching configuration files and environment profiles.", "Uses @EnableAutoConfiguration and reads META-INF/spring.factories to load conditional configuration classes.", ["Spring Boot", "Core"], "Very Common", "Medium"),
        ("SpringBootApplication Annotations", "What does @SpringBootApplication consist of?", "Consists of @Configuration (configuration class), @EnableAutoConfiguration (loads auto-configs), and @ComponentScan (scans packages).", "Acts as the standard entrypoint annotation for Spring Boot configurations and classpath sweeps.", ["Spring Boot", "Core"], "Very Common", "Easy"),
        ("Spring Security Architecture", "Explain Spring Security filter chain architecture.", "Uses DelegatingFilterProxy to intercept web requests and route them through a chain of Security Filters (UsernamePassword, Basic, Bearer).", "AuthenticationManager verifies credentials. SecurityContextHolder stores authenticated user details in ThreadLocal.", ["Spring Boot", "Security"], "Very Common", "Hard"),
        ("JWT Integration", "How do you integrate JWT authentication in Spring Boot?", "Create a custom JWT Filter extending OncePerRequestFilter, parse Bearer token from header, validate signature, and set user context.", "Saves state on client. Keeps APIs stateless, avoiding session storage lookups in microservice networks.", ["Spring Boot", "Security"], "Very Common", "Medium"),
        ("Transactional Annotation", "Explain @Transactional propagation and isolation levels.", "Propagation defines how transactions handle boundaries (e.g. REQUIRED, REQUIRES_NEW). Isolation defines visibility limits (e.g. READ_COMMITTED).", "REQUIRED uses active transaction or starts one. REQUIRES_NEW suspends active transaction, executing a new transaction block.", ["Spring Boot", "Data"], "Very Common", "Hard"),
        ("Spring Data JPA Cache", "Explain Level 1 and Level 2 Caching in Hibernate.", "L1 Cache: Session-level, transaction-scoped (always on). L2 Cache: SessionFactory-level, process-scoped (requires config).", "L1 caches entities queried in same transaction. L2 caching caches entities across transactions to optimize DB reads.", ["Spring Boot", "Data"], "Common", "Hard"),
        ("Microservice Communications", "Compare FeignClient, WebClient, and gRPC in Spring Boot.", "FeignClient: Declarative REST client. WebClient: Non-blocking, reactive REST client. gRPC: High-performance HTTP/2 binary client.", "Use Feign for simple REST APIs. Use WebClient for reactive pipelines. Use gRPC for low-latency microservice communications.", ["Spring Boot", "Microservices"], "Common", "Medium"),
        ("Spring Boot Actuator", "What is Spring Boot Actuator?", "Provides production-ready features (endpoints) to monitor health, database connection pools, logs, and thread metrics.", "Includes endpoints like /actuator/health, /actuator/metrics, and /actuator/threaddump.", ["Spring Boot", "Performance"], "Common", "Easy"),
        ("Spring Profiles", "How do you manage Spring Profiles across Dev, Test, and Prod?", "Use application-{profile}.properties/yml files, and activate them using spring.profiles.active property.", "Injects environment-specific configurations (URLs, credentials) dynamically during startup bootstrap sweeps.", ["Spring Boot", "Core"], "Common", "Easy"),
        ("DI Styles Comparison", "Compare Constructor, Setter, and Field Injection.", "Constructor: Recommended, allows immutability (final fields) and compile checks. Field: Simplest (@Autowired) but hard to unit test.", "Setter injection is optimal for optional dependencies. Constructor injection prevents circular dependency issues at compile-time.", ["Spring Boot", "Core"], "Common", "Easy"),
        ("Spring AOP", "What is Aspect-Oriented Programming (AOP) in Spring?", "A paradigm that allows modularizing cross-cutting concerns (logging, security, transactions) using Aspects, Joins, and Advices.", "Uses dynamic proxies (JDK dynamic proxy or CGLIB) to intercept method executions and inject advice code.", ["Spring Boot", "Core"], "Common", "Medium"),
        ("DispatcherServlet", "What is the role of DispatcherServlet?", "Acts as the Front Controller, intercepting all incoming HTTP requests and coordinating request dispatching across MVC controllers.", "Centralizes common configurations like locale resolution, exception handling, and handler mappings.", ["Spring Boot", "MVC"], "Common", "Medium"),
        ("Component vs Bean", "What is the difference between @Component and @Bean?", "@Component: Class-level annotation, auto-scanned by container. @Bean: Method-level annotation, defined manually in configurations.", "Use @Component for application classes. Use @Bean for configuring third-party libraries (e.g. RedisTemplate).", ["Spring Boot", "Core"], "Common", "Easy"),
        ("Spring Boot Starters", "What are Spring Boot Starter dependencies?", "Curated dependency descriptors that bundle commonly used library configurations under a single name (e.g. spring-boot-starter-web).", "Avoids manual dependency version management, automatically resolving compatible versions.", ["Spring Boot", "Core"], "Common", "Easy"),
        ("Exception Handling", "How do you handle exceptions globally in Spring Boot?", "Annotate a configuration class with @ControllerAdvice and write methods annotated with @ExceptionHandler.", "Intercepts specified exceptions thrown by controllers, returning structured error payloads with appropriate HTTP status codes.", ["Spring Boot", "MVC"], "Common", "Easy"),
        ("Properties Load Order", "What is the loading precedence of properties in Spring Boot?", "Command-line arguments override Environment variables, which override application.properties, which override bootstrap.properties.", "Allows external orchestrators (Docker/K8s configMaps) to override application properties dynamically on start.", ["Spring Boot", "Core"], "Common", "Medium"),
        ("Embedded Servers", "Compare Tomcat, Jetty, and Undertow in Spring Boot.", "Tomcat: Default servlet container, mature and reliable. Jetty: Lightweight. Undertow: High-performance, non-blocking architecture.", "Jetty is optimal for micro-containers. Undertow is optimal for high-throughput async processing.", ["Spring Boot", "Performance"], "Common", "Medium"),
        ("JPA Query Methods", "Compare JPA Query Methods and Native Queries.", "Query methods: Parsed from method name (findByTitle). Native: Regular SQL query written with nativeQuery=true.", "JPA Query methods generate HQL/JPQL. Native queries are db-vendor specific, skipping Hibernate abstractions.", ["Spring Boot", "Data"], "Common", "Easy"),
        ("Hibernate N plus 1", "How do you resolve the Hibernate N+1 query problem?", "Occurs when fetching parent entities triggers N additional queries for child collections. Resolved using Join Fetch queries.", "Specify JOIN FETCH in JPQL or use EntityGraphs to fetch parent and child entities in a single SQL JOIN.", ["Spring Boot", "Data"], "Very Common", "Hard"),
        ("Entity States", "Explain Transient, Persistent, Detached, and Removed entity states.", "Transient: New instance, not in DB. Persistent: Tracked by session, synced on commit. Detached: Session closed, entity untracked. Removed: Marked for deletion.", "Persistent modifications sync automatically. Detached objects require merge() to sync updates back to session.", ["Spring Boot", "Data"], "Common", "Medium"),
        ("Method Level Security", "What is @PreAuthorize and how does it work?", "Enables method-level authorization checks. Evaluates SpEL (Spring Expression Language) expressions before executing methods.", "Requires @EnableGlobalMethodSecurity annotation. Dynamic proxies intercept calls, checking user roles/permissions.", ["Spring Boot", "Security"], "Common", "Medium"),
        ("CORS Configuration", "How do you configure CORS in Spring Boot?", "Annotate controllers with @CrossOrigin, or write a WebMvcConfigurer bean to override addCorsMappings.", "CORS filters intercept pre-flight OPTIONS requests, returning matching Access-Control-Allow-Origin headers.", ["Spring Boot", "Security"], "Common", "Easy"),
        ("Integration Tests", "Compare @SpringBootTest and @WebMvcTest.", "@SpringBootTest: Loads full application context. @WebMvcTest: Instantiates only MVC layer components, mocking database layers.", "@WebMvcTest is faster for controller validation. @SpringBootTest is thorough for full database/service integrations.", ["Spring Boot", "Testing"], "Common", "Medium"),
        ("Prometheus Integration", "How do you export Spring Boot Actuator metrics to Prometheus?", "Include micrometer-registry-prometheus dependency. Actuator exposes metrics under /actuator/prometheus endpoint.", "Prometheus server scrapes this endpoint periodically, storing time-series counters and gauge statistics.", ["Spring Boot", "Performance"], "Common", "Medium"),
        ("Distributed Tracing", "What is Distributed Tracing and Sleuth/Micrometer in Spring Boot?", "Distributed tracing tracks request lifecycles across microservice networks. Sleuth/Micrometer generates Trace IDs and Span IDs.", "IDs append to HTTP headers (ZIPKIN format). Ingests tracing logs into dashboard collectors like Zipkin or Jaeger.", ["Spring Boot", "Performance"], "Common", "Hard"),
        ("Spring Batch", "Explain the architecture of Spring Batch.", "A framework for processing large volumes of records containing: JobLauncher, Job, Step (ItemReader, ItemProcessor, ItemWriter).", "Maintains job execution state in metadata tables, allowing restarts from failed checkpoints.", ["Spring Boot", "Batch Processing"], "Common", "Hard"),
        ("Spring Cloud Config", "What is Spring Cloud Config Server?", "A centralized configuration service that hosts environment properties in a Git repository, serving them to microservices.", "Allows updating configurations of running microservices dynamically without requiring application restarts.", ["Spring Boot", "Microservices"], "Common", "Hard"),
        ("Spring Cloud Gateway", "Explain Spring Cloud API Gateway routing.", "Routes requests to microservices using Predicates (match path, headers) and Filters (modify request/response headers).", "Built on Spring WebFlux (reactive netty), providing high throughput for routing and load-balancing services.", ["Spring Boot", "Microservices"], "Common", "Hard"),
        ("Circuit Breaker Resilience4j", "How does Circuit Breaker pattern work in microservices using Resilience4j?", "Monitors error rates of downstream API calls. Triages states: CLOSED (calls pass), OPEN (fail fast), HALF-OPEN (testing calls).", "Trips to OPEN if error rate exceeds threshold. Protects downstream services from cascading network failure.", ["Spring Boot", "Microservices"], "Very Common", "Hard"),
        ("Eureka Service Discovery", "Explain Eureka Service Discovery in microservices.", "Services register their IP/Port with Eureka server on startup. Clients fetch registry to locate microservice nodes.", "Eliminates hardcoded hostnames, resolving routing dynamically when auto-scaling service clusters.", ["Spring Boot", "Microservices"], "Common", "Medium"),
        ("Spring Events", "How do you implement event handling inside Spring application context?", "Publish events using ApplicationEventPublisher. Listen to events using methods annotated with @EventListener.", "Decouples application modules. By default, event execution is synchronous inside the publishing thread.", ["Spring Boot", "Core"], "Common", "Medium"),
        ("Spring Custom Starters", "How do you build a custom Spring Boot Starter?", "Create auto-configuration class, define condition annotations (@ConditionalOnClass), and register class in META-INF/spring.factories.", "Allows packaging shared enterprise components (common logging, security filters) for drop-in classpath imports.", ["Spring Boot", "Core"], "Common", "Hard"),
        ("Spring WebFlux", "What is Spring WebFlux and when should you use it?", "A reactive, non-blocking web framework built on Project Reactor. Runs on Netty. Uses Flux and Mono types.", "Optimal for high-concurrency streaming services or I/O-intensive apps. Ineffective if database queries are blocking.", ["Spring Boot", "Reactive"], "Common", "Hard"),
        ("Spring Data Redis", "How do you configure Redis cache in Spring Boot?", "Configure RedisConnectionFactory, define RedisCacheManager, and annotate service methods with @Cacheable.", "Stores method return values in Redis under specified keys. Subsequent calls return cached data directly.", ["Spring Boot", "Caching"], "Common", "Medium"),
        ("Spring Async", "How does the @Async annotation work in Spring?", "Executes annotated methods in a separate thread pool. Returns void or Future/CompletableFuture wrappers.", "Uses proxies to intercept calls and submit tasks to an TaskExecutor thread pool container.", ["Spring Boot", "Concurrency"], "Common", "Medium"),
        ("Spring Boot Validation", "How do you enforce input parameter validation in controllers?", "Annotate model parameters with @Valid, and use validation constraints (@NotNull, @Size, @Email) on DTO fields.", "Throws MethodArgumentNotValidException if validation checks fail, which global handlers intercept to format response logs.", ["Spring Boot", "MVC"], "Common", "Easy"),
        ("Spring Database Init", "How does Spring Boot initialize database schemas?", "Uses schema.sql and data.sql scripts located in resources, or database migration engines like Flyway.", "Autodetects DB dialects and runs SQL commands sequentially during initial application startup.", ["Spring Boot", "Data"], "Common", "Easy")
    ]
    
    # 6. Behavioral (40 unique situations)
    behavioral_list = [
        ("Technical Conflict", "Describe a time you had a technical disagreement with a peer.", "Discussed technical approaches using data-driven benchmarks. Reached compromise after documenting design pros and cons.", "Avoided emotional bias. Presented alternative architectural solutions to a team review to reach consensus.", ["Behavioral", "STAR"], "Very Common", "Easy"),
        ("Challenging Project", "Tell me about a challenging project you designed.", "Explain project scope, scale challenges, architectural tradeoffs, and performance tuning solutions (STAR framework).", "Highlighted personal contributions, system metrics improvements (e.g. latency cut by 40%), and lessons learned.", ["Behavioral", "STAR"], "Very Common", "Easy"),
        ("Handling Failure", "Tell me about a time you failed and what you learned.", "Outline a project delivery slip or code oversight. Focus on ownership, root cause analysis, and preventive measures implemented.", "Demonstrates accountability. Shows how failure prompted implementing test coverage safeguards to prevent repeat incidents.", ["Behavioral", "STAR"], "Very Common", "Easy"),
        ("Tight Deadlines", "How do you manage tight deadlines and shifting priorities?", "Identify critical path tasks, communicate risks to product owners, and scope down non-essential features.", "Remained calm, focused on high-priority deliverables, and organized daily syncs to align engineering efforts.", ["Behavioral", "STAR"], "Very Common", "Easy"),
        ("Customer Obsession", "Tell me about a time you went above and beyond for a customer.", "Identified a customer friction point (e.g. page checkout delay), investigated metrics, and fixed the bug outside normal sprint goals.", "Shows customer empathy. Quantified customer metrics improvements (e.g. conversion rates increased by 5%).", ["Behavioral", "STAR"], "Very Common", "Easy"),
        ("Production Outage", "Describe a time you had to debug a critical production outage under pressure.", "Outlined outage impacts, step-by-step triage sequence (mitigate first, root cause second), and post-mortem resolution.", "Communicated transparently with stakeholders, stabilized the system using a rollback, and added monitoring checks.", ["Behavioral", "STAR"], "Very Common", "Easy"),
        ("Constructive Feedback", "How do you handle negative performance reviews or constructive feedback?", "Listened actively without defensiveness, thanked the peer, and created an actionable improvement roadmap.", "Shows maturity and self-awareness. Discussed subsequent performance gains that verified positive changes.", ["Behavioral", "STAR"], "Very Common", "Easy"),
        ("Fast Tech Adoption", "Tell me about a time you had to learn a new technology quickly.", "Faced a project requiring a tech stack outside my domain (e.g. Go). Learned via guides, built prototypes, and shipped code in 2 weeks.", "Demonstrates agility and resourcefulness. Highlighted code review support that helped maintain quality bounds.", ["Behavioral", "STAR"], "Common", "Easy"),
        ("Influence Without Authority", "How do you convince peers to adopt a design pattern or tool?", "Built a working MVP to demonstrate performance gains, presented benchmarks, and hosted sharing sessions.", "Avoided authoritative demands. Encouraged developer interest by highlighting how the tool simplifies tasks.", ["Behavioral", "STAR"], "Common", "Easy"),
        ("Ambiguous Requirements", "How do you proceed when requirements are vague or ambiguous?", "Identify unknowns, draft assumption logs, and organize alignment sessions with product managers to clarify scope.", "Avoided assuming designs blindly. Created small prototypes to confirm product alignment before building core systems.", ["Behavioral", "STAR"], "Common", "Easy"),
        ("Disagree and Commit", "Tell me about a time you disagreed with a manager but committed anyway.", "Expressed concerns with data, but once the manager made a final decision, aligned 100% to execute it successfully.", "Prioritizes project delivery over personal ego. Monitored results to address any issues proactively.", ["Behavioral", "STAR"], "Very Common", "Easy"),
        ("Mentoring Teammates", "Describe a situation where you helped a struggling peer.", "Sat with the developer to identify skill blocks, shared debugging guides, and set weekly pair programming reviews.", "Maintained encouragement and respect. Tracked the developer's growth into an independent contributor.", ["Behavioral", "STAR"], "Common", "Easy"),
        ("Process Optimization", "Tell me about a process improvement initiative you started.", "Noticed slow manual deployment testing. Built a CI/CD automation script that ran checks concurrently, saving 2 hours per release.", "Saves developer time. Emphasizes productivity gains and reducing human verification error rates.", ["Behavioral", "STAR"], "Common", "Easy"),
        ("Tech Debt Tradeoff", "How do you balance tech debt cleanup versus feature delivery?", "Categorize tech debt impact (critical vs minor). Allocate 20% of sprint velocity to code cleanup, tracking metrics.", "Communicated technical constraints to product managers, demonstrating how cleanup accelerates future feature delivery.", ["Behavioral", "STAR"], "Common", "Easy"),
        ("Missed Deadline", "Tell me about a time you missed a project deadline.", "Communicated delivery slippage early to stakeholders, adjusted scope, and worked systematically to ship the delayed release.", "Took full ownership. Outlined post-mortem updates that improved future sprint planning accuracy.", ["Behavioral", "STAR"], "Common", "Easy"),
        ("Challenging Senior Decision", "Describe a time you challenged a senior engineer's architecture.", "Noticed a scaling bottleneck in a senior's design. Gathered load test benchmark reports and presented them in a private review.", "Maintained professional respect. Focused strictly on objective data, leading to a collaborative design adjustment.", ["Behavioral", "STAR"], "Common", "Easy"),
        ("Diversity Inclusion", "How do you foster a collaborative and inclusive team environment?", "Ensured every member had space to share ideas in reviews, and supported remote colleagues with async logs.", "Valued diverse viewpoints, helping build a psychologically safe workspace for engineering reviews.", ["Behavioral", "STAR"], "Common", "Easy"),
        ("Low Performing Peer", "How do you deal with a low-performing teammate during deliverables?", "Approached the peer privately to offer help, verified task allocations, and adjusted dependencies to keep projects on track.", "Maintained supportive teamwork while ensuring project delivery timelines were met.", ["Behavioral", "STAR"], "Common", "Easy"),
        ("Difficult Feedback", "Describe a time you had to deliver tough feedback to a peer.", "Offered feedback using constructive, actionable, and private structures (e.g. feedback on specific behaviors, not personality).", "Maintained peer support, helping them construct an action plan to address the performance gaps.", ["Behavioral", "STAR"], "Common", "Easy"),
        ("Launch With Known Bugs", "Have you ever launched a software release with known minor bugs?", "Yes. Checked bug impact severity. The bug had a simple fallback. Documented workarounds, and resolved it in the next patch.", "Demonstrates pragmatism. Balances launch delivery dates with system stability thresholds.", ["Behavioral", "STAR"], "Common", "Easy"),
        ("Speed vs Quality", "How do you manage the trade-off between shipping fast and writing perfect code?", "Aim for modular, tested code. Avoid over-engineering. Build simple designs first and iterate.", "Prioritizes delivering functional value while maintaining solid unit test boundaries to prevent regressions.", ["Behavioral", "STAR"], "Common", "Easy"),
        ("Cross Functional Work", "Describe a time you worked with product and design teams to ship a feature.", "Coordinates API requirements with designers and product managers to map user profiles to code boundaries.", "Ensured clean interface definitions, leading to a smooth frontend-backend integration release.", ["Behavioral", "STAR"], "Common", "Easy"),
        ("Midway Change Direction", "How do you adapt when requirements change halfway through a release?", "Assessed code impacts, reprioritized backlog items, and updated sprint boards to align developers.", "Maintained developer momentum, adjusting code architectures to support the new product specifications.", ["Behavioral", "STAR"], "Common", "Easy"),
        ("Proactive Bottleneck", "Tell me about a time you proactively fixed a system bottleneck.", "Noticed slow queries in logs. Analyzed tables using EXPLAIN, added indexes, and cached results, lowering DB load by 30%.", "Prevents production outages. Shows operational excellence and monitoring initiative.", ["Behavioral", "STAR"], "Common", "Easy"),
        ("Explain Tech NonTech", "How do you explain a complex API architecture to a non-technical manager?", "Avoided code jargon. Used visual real-world analogies (e.g., mail routing for message queues) and focused on business outcomes.", "Helped align business stakeholders, obtaining support for technical migrations.", ["Behavioral", "STAR"], "Common", "Easy"),
        ("Team Communication Breakdown", "Describe a time you resolved a communication breakdown in a team.", "Noticed conflicting code updates. Organized a alignment sweep, clarified ownership of services, and updated API docs.", "Aligned developers, reducing release blockages and improving team integration.", ["Behavioral", "STAR"], "Common", "Easy"),
        ("Out of Domain Ownership", "Tell me about a time you took ownership of a service outside your team's domain.", "Noticed a critical service failing. Cloned repo, debugged logs, found thread leak, and pushed patch to help owner team.", "Demonstrates leadership and bias for action. Prioritizes global system health over localized scope.", ["Behavioral", "STAR"], "Common", "Easy"),
        ("Admitting Mistake", "Describe a time you admitted a mistake to your manager.", "Accidentally ran query locking table. Cancelled process immediately, reported issue to manager, and drafted post-mortem.", "Shows integrity and transparency. Helped database team restrict direct query permissions in prod.", ["Behavioral", "STAR"], "Common", "Easy"),
        ("Advocating Migration", "How did you convince your team to migrate to a new framework?", "Compiled scaling limits of old framework, ran local microservice POCs in new framework, and showed response times comparisons.", "Led to an approved migration plan, resulting in 2x throughput gains and cleaner codebases.", ["Behavioral", "STAR"], "Common", "Easy"),
        ("Tedious Project Phases", "How do you stay motivated during tedious code migration tasks?", "Set small milestone targets, automated boring parsing steps, and kept team focused on final system health benefits.", "Maintained consistent output, completing migrations within scheduled deadlines.", ["Behavioral", "STAR"], "Common", "Easy"),
        ("Defining Success Metrics", "How do you define success metrics for code you write?", "Calculate execution latency, error rates, CPU overhead, and coverage. Align code with business KPIs.", "Ensures operational visibility. Allows tracking feature performance in dashboard logs.", ["Behavioral", "STAR"], "Common", "Easy"),
        ("Work Life Integration", "How do you manage high-stress releases without burning out?", "Prioritize tasks, delegate items, limit overtime to emergencies, and set clean boundaries for offline recharge.", "Maintained long-term productivity and positive team morale during high-intensity projects.", ["Behavioral", "STAR"], "Common", "Easy"),
        ("External Collaboration", "Describe a time you collaborated outside your team to clear a roadblock.", "Hit a block on database security settings. Contacted DBA team directly, analyzed logs together, and resolved configurations in an hour.", "Avoided waiting on ticket queues. Emphasizes active communication and collaboration.", ["Behavioral", "STAR"], "Common", "Easy"),
        ("Growth From Review", "Tell me about an improvement you made based on performance feedback.", "Received feedback on presenting designs. Attended sharing sweeps, learned communication layouts, and improved slides.", "Led to clean design approvals on subsequent projects, with positive feedback from reviewers.", ["Behavioral", "STAR"], "Common", "Easy"),
        ("Saying No", "Describe a time you had to say 'No' to a product request.", "Product requested real-time reports query in OLTP database. Explained database lock risks and suggested async exports instead.", "Maintained system stability. Collaborated to construct a safe reporting pipeline.", ["Behavioral", "STAR"], "Common", "Easy"),
        ("Champion Clean Code", "How do you champion refactoring practices in a team?", "Defined formatting rules, highlighted tech debt issues in code reviews, and held workshops on clean design patterns.", "Improved code quality metrics, reducing onboarding friction for new developers.", ["Behavioral", "STAR"], "Common", "Easy"),
        ("Internal Developer Tool", "Describe a helper tool you created for other developers.", "Created local database mock docker containers to help developers test query flows locally without shared sandboxes.", "Improved local testing speeds, saving 30 minutes of setup time per developer.", ["Behavioral", "STAR"], "Common", "Easy"),
        ("Adapting Reorganization", "How did you handle a major organizational restructure?", "Aligned with new team leads, audited existing projects, and updated backlogs to fit new team deliverables.", "Maintained delivery momentum, adapting to new processes with positivity.", ["Behavioral", "STAR"], "Common", "Easy"),
        ("Release Blockage Calm", "Describe a time you handled a critical release blockage with calm leadership.", "Found a severe bug on release day. Halted deployment, coordinated team to isolate bug, and pushed a patch in 20 minutes.", "Avoided panic. Kept stakeholders aligned and system stable.", ["Behavioral", "STAR"], "Common", "Easy"),
        ("Continuous Learning", "How do you keep your technical skills updated?", "Follow system design blogs, build prototype apps in new versions (e.g. Java 21), and read technical books.", "Brings modern, optimized patterns into production systems (e.g. adopting virtual threads).", ["Behavioral", "STAR"], "Common", "Easy")
    ]
    
    # Map and append unique question IDs and data
    idx = 1
    
    # 1. Add DSA
    for name, desc, ans, exp, tags, freq, diff in dsa_list:
        questions.append({
            "question_id": idx,
            "category": "DSA",
            "difficulty": diff,
            "question": f"Optimal Solution for '{name}': {desc}",
            "answer": ans,
            "explanation": exp,
            "tags": tags,
            "frequency": freq
        })
        idx += 1
        
    # 2. Add DBMS
    for name, desc, ans, exp, tags, freq, diff in dbms_list:
        questions.append({
            "question_id": idx,
            "category": "DBMS",
            "difficulty": diff,
            "question": f"Explain '{name}': {desc}",
            "answer": ans,
            "explanation": exp,
            "tags": tags,
            "frequency": freq
        })
        idx += 1
        
    # 3. Add OS
    for name, desc, ans, exp, tags, freq, diff in os_list:
        questions.append({
            "question_id": idx,
            "category": "OS",
            "difficulty": diff,
            "question": f"Explain '{name}': {desc}",
            "answer": ans,
            "explanation": exp,
            "tags": tags,
            "frequency": freq
        })
        idx += 1
        
    # 4. Add HLD
    for name, desc, ans, exp, tags, freq, diff in hld_list:
        questions.append({
            "question_id": idx,
            "category": "System Design",
            "difficulty": diff,
            "question": f"System Design: '{name}' - {desc}",
            "answer": ans,
            "explanation": exp,
            "tags": tags,
            "frequency": freq
        })
        idx += 1
        
    # 5. Add LLD
    for name, desc, ans, exp, tags, freq, diff in lld_list:
        questions.append({
            "question_id": idx,
            "category": "System Design",
            "difficulty": diff,
            "question": f"Low-Level Design (LLD): '{name}' - {desc}",
            "answer": ans,
            "explanation": exp,
            "tags": tags,
            "frequency": freq
        })
        idx += 1
        
    # 6. Add Java
    for name, desc, ans, exp, tags, freq, diff in java_list:
        questions.append({
            "question_id": idx,
            "category": "Java",
            "difficulty": diff,
            "question": f"Java: '{name}' - {desc}",
            "answer": ans,
            "explanation": exp,
            "tags": tags,
            "frequency": freq
        })
        idx += 1
        
    # 7. Add Spring Boot
    for name, desc, ans, exp, tags, freq, diff in spring_list:
        questions.append({
            "question_id": idx,
            "category": "Spring Boot",
            "difficulty": diff,
            "question": f"Spring Boot: '{name}' - {desc}",
            "answer": ans,
            "explanation": exp,
            "tags": tags,
            "frequency": freq
        })
        idx += 1
        
    # 8. Add Behavioral
    for name, desc, ans, exp, tags, freq, diff in behavioral_list:
        questions.append({
            "question_id": idx,
            "category": "Behavioral",
            "difficulty": diff,
            "question": f"Behavioral: '{name}' - {desc}",
            "answer": ans,
            "explanation": exp,
            "tags": tags,
            "frequency": freq
        })
        idx += 1
        
    print(f"Generated {len(questions)} total unique SDE questions.")
    
    # Save CSV
    headers = ["question_id", "company_role_id", "category", "difficulty", "question", "answer", "explanation", "tags", "frequency"]
    csv_rows = []
    for q in questions:
        csv_rows.append({
            "question_id": q["question_id"],
            "company_role_id": 1, # default Blinkit SDE
            "category": q["category"],
            "difficulty": q["difficulty"],
            "question": q["question"],
            "answer": q["answer"],
            "explanation": q["explanation"],
            "tags": str(q["tags"]),
            "frequency": q["frequency"]
        })
        
    os.makedirs(HIRING_CSV_DIR, exist_ok=True)
    with open(os.path.join(HIRING_CSV_DIR, "interview_questions.csv"), mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(csv_rows)
        
    # Save JSON
    json_rows = []
    for q in questions:
        json_rows.append({
            "category": q["category"],
            "difficulty": q["difficulty"],
            "question": q["question"],
            "answer": q["answer"],
            "explanation": q["explanation"],
            "tags": q["tags"],
            "frequency": q["frequency"]
        })
        
    json_dir = os.path.join(DATASETS_DIR, "interview_questions")
    os.makedirs(json_dir, exist_ok=True)
    with open(os.path.join(json_dir, "interview_questions.json"), mode='w', encoding='utf-8') as f:
        json.dump(json_rows, f, indent=4)
        
    print("Interview Questions files successfully saved.")
        
    print(f"Generated {len(questions)} total questions.")
    
    # Save CSV
    headers = ["question_id", "company_role_id", "category", "difficulty", "question", "answer", "explanation", "tags", "frequency"]
    csv_rows = []
    for q in questions:
        csv_rows.append({
            "question_id": q["question_id"],
            "company_role_id": 1, # default Blinkit SDE
            "category": q["category"],
            "difficulty": q["difficulty"],
            "question": q["question"],
            "answer": q["answer"],
            "explanation": q["explanation"],
            "tags": str(q["tags"]),
            "frequency": q["frequency"]
        })
        
    os.makedirs(HIRING_CSV_DIR, exist_ok=True)
    with open(os.path.join(HIRING_CSV_DIR, "interview_questions.csv"), mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(csv_rows)
        
    # Save JSON
    json_rows = []
    for q in questions:
        json_rows.append({
            "category": q["category"],
            "difficulty": q["difficulty"],
            "question": q["question"],
            "answer": q["answer"],
            "explanation": q["explanation"],
            "tags": q["tags"],
            "frequency": q["frequency"]
        })
        
    json_dir = os.path.join(DATASETS_DIR, "interview_questions")
    os.makedirs(json_dir, exist_ok=True)
    with open(os.path.join(json_dir, "interview_questions.json"), mode='w', encoding='utf-8') as f:
        json.dump(json_rows, f, indent=4)
        
    print("Interview Questions files successfully saved.")


# ==============================================================================
# PART 2: LEARNING RESOURCES GENERATOR (120+ Resources)
# ==============================================================================
def generate_learning_resources():
    print("Generating 120+ Learning Resources...")
    resources = []
    res_id = 1
    
    platforms = ["YouTube", "Udemy", "Coursera", "LeetCode", "GeeksForGeeks", "GitHub", "Medium", "System Design Primer"]
    
    # Generate 5 resources for each of the 26 skills
    for skill_id, skill_name in SKILLS_MAP.items():
        # Resource 1: Getting Started Video Playlist (Free)
        resources.append({
            "resource_id": res_id,
            "title": f"Complete {skill_name} Beginner's Playlist 2026",
            "resource_type": "Playlist",
            "topic": skill_name,
            "skill_id": skill_id,
            "url": f"https://youtube.com/results?search_query={skill_name.lower().replace(' ', '+')}+tutorial",
            "platform": "YouTube",
            "difficulty": "Beginner",
            "duration_hours": 15.0,
            "is_free": "True",
            "rating": 4.7,
            "notes": f"High-quality structured YouTube playlist covering fundamental concepts of {skill_name} step-by-step."
        })
        res_id += 1
        
        # Resource 2: Deep Dive Practice Sheet / Sandbox
        resources.append({
            "resource_id": res_id,
            "title": f"Mastering {skill_name} Hands-On Exercises",
            "resource_type": "Practice Platform",
            "topic": skill_name,
            "skill_id": skill_id,
            "url": f"https://github.com/topics/{skill_name.lower().replace(' ', '-')}-exercises",
            "platform": "GitHub",
            "difficulty": "Intermediate",
            "duration_hours": 20.0,
            "is_free": "True",
            "rating": 4.8,
            "notes": f"GitHub repository containing coding assignments, templates, and compiler-ready test cases for {skill_name} practice."
        })
        res_id += 1
        
        # Resource 3: Comprehensive Udemy / Coursera Specialization
        resources.append({
            "resource_id": res_id,
            "title": f"{skill_name} Certification & Production Architecture",
            "resource_type": "Course",
            "topic": skill_name,
            "skill_id": skill_id,
            "url": f"https://www.coursera.org/search?query={skill_name.lower()}",
            "platform": "Coursera",
            "difficulty": "Advanced",
            "duration_hours": 45.0,
            "is_free": "False",
            "rating": 4.9,
            "notes": f"Comprehensive masterclass on {skill_name} led by industry professionals with peer-reviewed grading."
        })
        res_id += 1
        
        # Resource 4: Official Technical Documentation
        resources.append({
            "resource_id": res_id,
            "title": f"{skill_name} Reference Manual and Best Practices",
            "resource_type": "Documentation",
            "topic": skill_name,
            "skill_id": skill_id,
            "url": f"https://devdocs.io/{skill_name.lower().replace(' ', '-')}",
            "platform": "Documentation",
            "difficulty": "Beginner",
            "duration_hours": 8.0,
            "is_free": "True",
            "rating": 4.9,
            "notes": f"Official documentation, API references, configuration guides, and environment setups for {skill_name} engineers."
        })
        res_id += 1
        
        # Resource 5: Interview Cheat Sheet / Articles
        resources.append({
            "resource_id": res_id,
            "title": f"Top 50 {skill_name} Interview Questions & Answers",
            "resource_type": "Article",
            "topic": skill_name,
            "skill_id": skill_id,
            "url": f"https://geeksforgeeks.org/{skill_name.lower().replace(' ', '-')}-interview-prep",
            "platform": "GeeksForGeeks",
            "difficulty": "Intermediate",
            "duration_hours": 4.0,
            "is_free": "True",
            "rating": 4.6,
            "notes": f"Curated list of frequently asked conceptual and coding questions for cracking {skill_name} interviews."
        })
        res_id += 1

    print(f"Generated {len(resources)} total resources.")
    
    # Save CSV
    headers = ["resource_id", "title", "resource_type", "topic", "skill_id", "url", "platform", "difficulty", "duration_hours", "is_free", "rating", "notes"]
    os.makedirs(LEARNING_CSV_DIR, exist_ok=True)
    with open(os.path.join(LEARNING_CSV_DIR, "learning_resources.csv"), mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(resources)
        
    # Save JSON
    json_rows = []
    for r in resources:
        json_rows.append({
            "title": r["title"],
            "resource_type": r["resource_type"],
            "topic": r["topic"],
            "url": r["url"],
            "platform": r["platform"],
            "difficulty": r["difficulty"],
            "duration_hours": r["duration_hours"],
            "is_free": r["is_free"] == "True",
            "rating": r["rating"],
            "notes": r["notes"]
        })
        
    json_dir = os.path.join(DATASETS_DIR, "resources")
    os.makedirs(json_dir, exist_ok=True)
    with open(os.path.join(json_dir, "learning_resources.json"), mode='w', encoding='utf-8') as f:
        json.dump(json_rows, f, indent=4)
        
    print("Learning Resources files successfully saved.")


# ==============================================================================
# PART 3: PROJECTS GENERATOR (75+ Projects)
# ==============================================================================
def generate_projects():
    print("Generating 75+ Projects and Mappings...")
    projects = []
    mapping = []
    
    mapping_id = 1
    
    # Let's define 75 high-quality SDE projects
    project_seeds = [
        ("Distributed Message Queue", "Build a high-throughput message broker that supports publish-subscribe patterns and partition offsets.", "Advanced", 30, ["Go", "Kafka", "PostgreSQL", "Distributed Systems"], "Demonstrates distributed message routing, thread-safe queuing, and custom TCP protocols."),
        ("Distributed Key-Value Store", "Create a partitioned, replicated key-value storage engine using Raft consensus protocol.", "Advanced", 40, ["Go", "Redis", "Distributed Systems", "System Design"], "Demonstrates consensus protocols, socket connections, and disk storage management."),
        ("API Gateway with Dynamic Rate Limiting", "Implement a reverse proxy engine that routes requests and throttles requests using token bucket algorithm in Redis.", "Intermediate", 15, ["Go", "Redis", "Docker", "System Design"], "Demonstrates middleware development, rate limiting, and reverse proxy routing."),
        ("Distributed Transaction Orchestrator (Saga)", "Write a coordinator service that manages multi-service updates using Saga pattern (compensating transactions).", "Advanced", 25, ["Java", "Spring Boot", "Kafka", "Microservices"], "Demonstrates event-driven transactional consistency, error boundaries, and state machines."),
        ("SaaS Multi-Tenant Database Router", "Create a Java service that dynamically switches data sources based on tenant request headers using Hibernate/Postgres.", "Intermediate", 20, ["Java", "Spring Boot", "PostgreSQL", "MySQL"], "Demonstrates tenant isolation patterns, pool pooling, and reflection configurations."),
        ("Log Aggregation & Search Pipeline", "Create a high-speed log ingestion shipper that indexes system events into Elasticsearch database.", "Advanced", 21, ["Python", "ElasticSearch", "Kafka", "Docker"], "Demonstrates search query parsing, real-time log ingestion, and database indexing."),
        ("Websocket Chat Server at Scale", "Implement a server that handles 50,000 active websocket connections, broadcasts messages via Redis pub-sub.", "Advanced", 18, ["NodeJS", "TypeScript", "Redis", "Websocket"], "Demonstrates async connection management, channels, and low-latency network I/O."),
        ("Job Scheduler Cron Engine", "Build an offline task scheduler that queues tasks in PostgreSQL and executes them using worker threads.", "Intermediate", 14, ["Go", "PostgreSQL", "MySQL", "Docker"], "Demonstrates concurrent worker patterns, transactional locking, and task queues."),
        ("E-Commerce Inventory Lock Manager", "Build an inventory checkout blocker service using Redis Distributed Locks (Redlock) to prevent overselling.", "Intermediate", 12, ["Java", "Spring Boot", "Redis", "Microservices"], "Demonstrates concurrency control, lock lease handling, and caching."),
        ("Ride-Sharing Driver Matching Service", "Implement a driver selection backend using spatial indexes (Uber H3 Geo-hashing) and WebSocket communication.", "Advanced", 28, ["Go", "Redis", "PostgreSQL", "System Design"], "Demonstrates geospatial queries, real-time telemetry pipelines, and fast matching loops."),
        ("Video Streaming CDN Cache", "Design and run a cache server that stores video segments and serves them via HTTP Range requests with LRU eviction.", "Advanced", 30, ["Go", "Docker", "AWS", "System Design"], "Demonstrates storage design, network chunking, and memory eviction caching."),
        ("Ad-Click Analytics Dashboard", "Build a stream processor that aggregates ad-click events per minute and displays metrics on a frontend chart.", "Intermediate", 16, ["React", "NodeJS", "Kafka", "ElasticSearch"], "Demonstrates stream joins, time-series data aggregation, and real-time frontend charts."),
        ("Distributed Web Crawler", "Build a multithreaded link indexer that respects robots.txt and crawls sites concurrently using BFS.", "Intermediate", 15, ["Python", "PostgreSQL", "Redis", "Distributed Systems"], "Demonstrates crawler state management, duplicate filtering, and rate limiting."),
        ("Search Auto-complete System", "Create a prefix-matching auto-complete service using Trie data structures and high-speed memory caching.", "Intermediate", 14, ["NodeJS", "TypeScript", "Redis", "React"], "Demonstrates prefix trees, input debouncing, and search indexing."),
        ("Real-Time Leaderboard System", "Build a high-performance gaming scoreboard using Redis Sorted Sets (ZSET) updating 10,000 ranks per second.", "Easy", 10, ["Python", "Redis", "Docker"], "Demonstrates Redis data structures, sorted set updates, and score scoring logic."),
        ("Offline-first Note Syncing App", "Develop an Android notes app that caches edits in SQLite and syncs with backend via background workers.", "Intermediate", 20, ["Kotlin", "Android", "PostgreSQL", "Mobile"], "Demonstrates offline database synchronization, network change listeners, and background sync."),
        ("Personal Finance Tracker Dashboard", "Build a dashboard showing income, expenses, monthly budgets, and chart visualizations using Django and React.", "Easy", 12, ["Python", "Django", "React", "MySQL"], "Demonstrates basic full-stack APIs, database CRUD operations, and graphing charts.")
    ]
    
    # Expand to 75 projects programmatically
    idx = 1
    for name, desc, diff, days, skills, outcome in project_seeds:
        projects.append({
            "project_id": idx,
            "project_name": name,
            "description": desc,
            "difficulty": diff,
            "estimated_days": days,
            "skills_covered": skills,
            "outcome": outcome
        })
        idx += 1
        
    for i in range(75 - len(projects)):
        skill_subset = [SKILLS_MAP[i % 26 + 1], SKILLS_MAP[(i+5) % 26 + 1]]
        projects.append({
            "project_id": idx,
            "project_name": f"Production SDE Project #{idx}: {skill_subset[0]} Application",
            "description": f"Build a production-ready application demonstrating advanced patterns in {skill_subset[0]} and {skill_subset[1]} integration.",
            "difficulty": "Intermediate" if i % 2 == 0 else "Advanced",
            "estimated_days": 15 + (i % 20),
            "skills_covered": skill_subset,
            "outcome": f"Demonstrates robust implementation of {skill_subset[0]} features, environment setup, and deployment configurations."
        })
        idx += 1
        
    # Build Project Skill Mapping CSV rows
    for p in projects:
        p_id = p["project_id"]
        for s_name in p["skills_covered"]:
            if s_name in REVERSE_SKILLS_MAP:
                s_id = REVERSE_SKILLS_MAP[s_name]
                mapping.append({
                    "id": mapping_id,
                    "project_id": p_id,
                    "skill_id": s_id
                })
                mapping_id += 1

    print(f"Generated {len(projects)} total projects.")
    print(f"Generated {len(mapping)} total project-skill mappings.")
    
    # Save CSV: projects_master.csv
    headers_proj = ["project_id", "project_name", "description", "difficulty", "estimated_days", "outcome"]
    os.makedirs(LEARNING_CSV_DIR, exist_ok=True)
    with open(os.path.join(LEARNING_CSV_DIR, "projects_master.csv"), mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers_proj)
        writer.writeheader()
        for p in projects:
            writer.writerow({
                "project_id": p["project_id"],
                "project_name": p["project_name"],
                "description": p["description"],
                "difficulty": p["difficulty"],
                "estimated_days": p["estimated_days"],
                "outcome": p["outcome"]
            })
            
    # Save CSV: project_skill_mapping.csv
    headers_map = ["id", "project_id", "skill_id"]
    with open(os.path.join(LEARNING_CSV_DIR, "project_skill_mapping.csv"), mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers_map)
        writer.writeheader()
        writer.writerows(mapping)
        
    # Save JSON: projects.json
    json_rows = []
    for p in projects:
        json_rows.append({
            "project_name": p["project_name"],
            "description": p["description"],
            "difficulty": p["difficulty"],
            "estimated_days": p["estimated_days"],
            "skills_covered": p["skills_covered"],
            "outcome": p["outcome"]
        })
        
    json_dir = os.path.join(DATASETS_DIR, "projects")
    os.makedirs(json_dir, exist_ok=True)
    with open(os.path.join(json_dir, "projects.json"), mode='w', encoding='utf-8') as f:
        json.dump(json_rows, f, indent=4)
        
    print("Projects files successfully saved.")


# ==============================================================================
# MAIN RUNNER
# ==============================================================================
if __name__ == "__main__":
    print("\n" + "="*50)
    print("CAREERCOMPASS AI — DATASETS SCALE EXPANSION PIPELINE")
    print("="*50)
    generate_interview_questions()
    print("-"*50)
    generate_learning_resources()
    print("-"*50)
    generate_projects()
    print("="*50)
    print("All expanded datasets successfully generated!")
    print("="*50 + "\n")
