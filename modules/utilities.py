def flatten_list(li):
    return [item for sublist in li for item in sublist]


def balanced_brackets(s):
    pairs = {"(": ")"}
    stack = []
    for c in s:
        if c not in "()":
            continue
        if c in "(":
            stack.append(c)
        elif stack and c == pairs[stack[-1]]:
            stack.pop()
        else:
            return False
    return len(stack) == 0

# return elements unique between two lists


def unique_elements(list1, list2):
    return list(set(list1).symmetric_difference(set(list2)))
