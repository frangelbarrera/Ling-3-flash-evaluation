# Phase 2 — Prompts Used

## MMLU + GPQA Questions

### mmlu_cs_1 (Computer Science)
```
Which data structure uses LIFO (Last-In-First-Out) ordering?
A. Queue
B. Stack
C. Linked List
D. Tree
Expected: B
```

### mmlu_cs_2 (Computer Science)
```
What is the time complexity of binary search on a sorted array of n elements?
A. O(n)
B. O(log n)
C. O(n log n)
D. O(1)
Expected: B
```

### mmlu_cs_3 (Computer Science)
```
In Python, which keyword is used to define a function?
A. func
B. define
C. def
D. function
Expected: C
```

### mmlu_cs_4 (Computer Science)
```
What does 'ACID' stand for in database transactions?
A. Atomicity, Consistency, Isolation, Durability
B. Atomicity, Concurrency, Isolation, Distribution
C. Availability, Consistency, Isolation, Durability
D. Atomicity, Caching, Indexing, Distribution
Expected: A
```

### mmlu_cs_5 (Computer Science)
```
Which sorting algorithm has the best average time complexity?
A. Bubble Sort
B. Quick Sort
C. Insertion Sort
D. Selection Sort
Expected: B
```

### mmlu_math_1 (Math)
```
What is the derivative of x^3 with respect to x?
A. x^2
B. 3x^2
C. 3x
D. x^3/3
Expected: B
```

### mmlu_math_2 (Math)
```
What is the integral of 1/x dx?
A. x + C
B. ln|x| + C
C. 1/x^2 + C
D. x^2/2 + C
Expected: B
```

### mmlu_math_3 (Math)
```
If f(x) = 2x + 3, what is f(5)?
A. 10
B. 13
C. 15
D. 8
Expected: B
```

### mmlu_math_4 (Math)
```
What is the value of pi to 2 decimal places?
A. 3.14
B. 3.15
C. 3.13
D. 3.16
Expected: A
```

### mmlu_math_5 (Math)
```
What is log_2(8)?
A. 2
B. 3
C. 4
D. 8
Expected: B
```

### mmlu_hist_1 (History)
```
In what year did World War II end?
A. 1943
B. 1944
C. 1945
D. 1946
Expected: C
```

### mmlu_hist_2 (History)
```
Who was the first president of the United States?
A. Thomas Jefferson
B. George Washington
C. John Adams
D. Benjamin Franklin
Expected: B
```

### mmlu_hist_3 (History)
```
The French Revolution began in what year?
A. 1776
B. 1789
C. 1799
D. 1804
Expected: B
```

### mmlu_hist_4 (History)
```
Who wrote the Communist Manifesto with Karl Marx?
A. Vladimir Lenin
B. Friedrich Engels
C. Leon Trotsky
D. Joseph Stalin
Expected: B
```

### mmlu_hist_5 (History)
```
In what year did the Berlin Wall fall?
A. 1987
B. 1988
C. 1989
D. 1990
Expected: C
```

### mmlu_med_1 (Medicine)
```
How many chambers does the human heart have?
A. 2
B. 3
C. 4
D. 5
Expected: C
```

### mmlu_med_2 (Medicine)
```
What is the largest organ in the human body?
A. Heart
B. Liver
C. Skin
D. Brain
Expected: C
```

### mmlu_med_3 (Medicine)
```
Which vitamin is produced when skin is exposed to sunlight?
A. Vitamin A
B. Vitamin C
C. Vitamin D
D. Vitamin K
Expected: C
```

### mmlu_med_4 (Medicine)
```
What is the normal resting heart rate range for adults (beats per minute)?
A. 40-60
B. 60-100
C. 100-140
D. 140-180
Expected: B
```

### mmlu_med_5 (Medicine)
```
Which blood type is the universal donor?
A. A+
B. B+
C. O-
D. AB+
Expected: C
```

### mmlu_law_1 (Law)
```
What does 'habeas corpus' literally translate to?
A. You have the body
B. Let the body stand
C. Produce the body
D. The body of law
Expected: A
```

### mmlu_law_2 (Law)
```
How many justices serve on the US Supreme Court?
A. 7
B. 8
C. 9
D. 10
Expected: C
```

### mmlu_law_3 (Law)
```
What is the standard of proof in a criminal case?
A. Preponderance of evidence
B. Clear and convincing
C. Beyond reasonable doubt
D. Probable cause
Expected: C
```

### mmlu_law_4 (Law)
```
Which amendment to the US Constitution protects against self-incrimination?
A. 1st
B. 4th
C. 5th
D. 6th
Expected: C
```

### mmlu_law_5 (Law)
```
What is the legal age to vote in the United States?
A. 16
B. 18
C. 21
D. 25
Expected: B
```

### gpqa_1 (GPQA)
```
In quantum mechanics, what is the expectation value of the position operator x in a stationary state?
A. It equals the classical position
B. It is always zero for symmetric potentials
C. It is time-independent and equals ∫ψ*xψdx
D. It depends on the momentum
Expected: C
```

### gpqa_2 (GPQA)
```
Which of the following is NOT a consequence of general relativity?
A. Gravitational time dilation
B. Light bending near massive objects
C. Frame dragging
D. Quantum entanglement of particles
Expected: D
```

### gpqa_3 (GPQA)
```
In organic chemistry, what is the hybridization of the carbon atom in methane (CH4)?
A. sp
B. sp2
C. sp3
D. sp3d
Expected: C
```

### gpqa_4 (GPQA)
```
What is the pH of a 0.001 M solution of HCl?
A. 1
B. 2
C. 3
D. 4
Expected: C
```

### gpqa_5 (GPQA)
```
In evolutionary biology, what does 'fitness' refer to in the Darwinian sense?
A. Physical strength
B. Reproductive success
C. Survival time
D. Speed of motion
Expected: B
```

### gpqa_6 (GPQA)
```
What is the entropy change when 1 mole of ideal gas expands isothermally from V to 2V?
A. R ln 2
B. 2R
C. R
D. 0
Expected: A
```

### gpqa_7 (GPQA)
```
Which of these is a tumor suppressor gene?
A. RAS
B. MYC
C. p53
D. HER2
Expected: C
```

### gpqa_8 (GPQA)
```
In signal processing, what does the Nyquist theorem state about sampling?
A. Sample at twice the maximum frequency
B. Sample at the maximum frequency
C. Sample at half the maximum frequency
D. Sample at any rate
Expected: A
```

### gpqa_9 (GPQA)
```
What is the relationship between the Gibbs free energy G and the equilibrium constant K?
A. ΔG = -RT ln K
B. ΔG = RT ln K
C. ΔG = -K ln RT
D. ΔG = K/RT
Expected: A
```

### gpqa_10 (GPQA)
```
In neuroscience, what is the primary excitatory neurotransmitter in the brain?
A. GABA
B. Glutamate
C. Dopamine
D. Serotonin
Expected: B
```


## AIME Problems

### aime_1
```
Find the number of positive integers n ≤ 1000 such that n^2 + 9 is divisible by 7.
Expected: 271
```

### aime_2
```
A sequence is defined by a_1 = 1, a_2 = 1, and a_n = a_{n-1} + a_{n-2} for n ≥ 3. Find a_10.
Expected: 55
```

### aime_3
```
Find the sum of all positive integers n such that n^2 - 19n + 99 is a perfect square.
Expected: 38
```

### aime_4
```
How many ways can 7 people be seated around a circular table?
Expected: 720
```

### aime_5
```
Find the remainder when 2^100 is divided by 7.
Expected: 2
```


## HumanEval + MBPP Problems

### humaneval_1
```
def has_close_elements(numbers: List[float], threshold: float) -> bool:
    """ Check if any two numbers in the list are closer than threshold. """
    # implementation here
    pass

# Write the complete function.
```

### humaneval_2
```
def separate_paren_groups(paren_string: str) -> List[str]:
    """ Split string into separate balanced paren groups. """
    # implementation here
    pass

# Write the complete function.
```

### humaneval_3
```
def truncate_number(number: float) -> float:
    """ Return the decimal part of a positive number. """
    # implementation here
    pass

# Write the complete function.
```

### humaneval_4
```
def below_zero(operations: List[int]) -> bool:
    """ Return True if balance goes below zero at any point. """
    # implementation here
    pass

# Write the complete function.
```

### humaneval_5
```
def mean_absolute_deviation(numbers: List[float]) -> float:
    """ Calculate MAD: average of absolute deviations from mean. """
    # implementation here
    pass

# Write the complete function.
```

### humaneval_6
```
def intersperse(numbers: List[int], delimeter: int) -> List[int]:
    """ Insert delimeter between each pair of numbers. """
    # implementation here
    pass

# Write the complete function.
```

### humaneval_7
```
def parse_nested_parens(paren_string: str) -> List[int]:
    """ Return list of max nesting depths for each group. """
    # implementation here
    pass

# Write the complete function.
```

### humaneval_8
```
def string_to_float(s: str) -> float:
    """ Convert string to float, return 0 on failure. """
    # implementation here
    pass

# Write the complete function.
```

### humaneval_9
```
def count_distinct_chars(s: str) -> int:
    """ Count distinct alphabetic chars (case insensitive). """
    # implementation here
    pass

# Write the complete function.
```

### humaneval_10
```
def is_palindrome(s: str) -> bool:
    """ Check if string is a palindrome (case insensitive, alphanumeric only). """
    # implementation here
    pass

# Write the complete function.
```

### mbpp_1
```
Write a Python function `is_monotonic(sequence)` that returns True if the sequence is monotonic (either entirely non-increasing or non-decreasing). Include a docstring and 2 test cases with assert.
```

### mbpp_2
```
Write a Python function `find_kth_largest(nums, k)` that returns the k-th largest element. Include a docstring and 2 test cases.
```

### mbpp_3
```
Write a Python function `are_anagrams(s1, s2)` that checks if two strings are anagrams (case insensitive, ignore non-alpha). Include 2 test cases.
```

### mbpp_4
```
Write a Python function `count_vowels(s)` that returns the count of vowels in a string. Include 2 test cases.
```

### mbpp_5
```
Write a Python function `merge_sorted_lists(a, b)` that merges two sorted lists into one sorted list. Include 2 test cases.
```

### mbpp_6
```
Write a Python function `binary_search(arr, target)` that returns the index of target in sorted arr, or -1. Include 2 test cases.
```

### mbpp_7
```
Write a Python function `is_prime(n)` that returns True if n is prime. Include 2 test cases.
```

### mbpp_8
```
Write a Python function `reverse_words(s)` that reverses the word order in a string. Include 2 test cases.
```

### mbpp_9
```
Write a Python function `fibonacci(n)` that returns the n-th Fibonacci number (F(0)=0, F(1)=1). Include 2 test cases.
```

### mbpp_10
```
Write a Python function `compress_string(s)` that does basic run-length encoding (e.g. 'AAABB' -> 'A3B2'). Include 2 test cases.
```


## BBH Problems

### bbh_1
```
A murder happened in a house. The suspects are: Alice (clean record, in kitchen at 9pm), Bob (motive, in bedroom at 9pm), Charlie (no alibi, was watching TV). Who is most likely the murderer based on these facts?
Expected: Charlie (no alibi)
```

### bbh_2
```
If all A are B, and some B are C, can we conclude some A are C? Explain.
Expected: No - we cannot conclude that. We know some B are C, but those B might all be non-A.
```

### bbh_3
```
Three boxes: one with gold, two with silver. You pick box 1. Host opens box 3 (silver). Should you switch to box 2? Explain.
Expected: Yes, you should switch. This is the Monty Hall problem - switching gives 2/3 chance of winning vs 1/3 staying.
```

### bbh_4
```
What comes next in the sequence: 2, 6, 12, 20, 30, ?
Expected: 42 (differences are 4,6,8,10,12)
```

### bbh_5
```
If today is Wednesday, what day will it be 100 days from now?
Expected: Friday (100 mod 7 = 2, Wednesday + 2 = Friday)
```

### bbh_6
```
Solve: A bat and ball cost $1.10. The bat costs $1.00 more than the ball. How much does the ball cost?
Expected: $0.05 (ball=x, bat=x+1.00, 2x+1.00=1.10, x=0.05)
```

### bbh_7
```
In a race, you overtake the person in 2nd place. What position are you in now?
Expected: 2nd (you took their place, not 1st)
```

### bbh_8
```
A farmer has 17 sheep. All but 9 run away. How many sheep does the farmer have left?
Expected: 9 (all but 9 means 9 remain)
```

### bbh_9
```
If you have 3 apples and take away 2, how many apples do you have?
Expected: 2 (you took them)
```

### bbh_10
```
What is the next number: 1, 11, 21, 1211, ?
Expected: 111221 (each term describes the previous: 1='one 1'=11, 11='two 1s'=21, etc.)
```

