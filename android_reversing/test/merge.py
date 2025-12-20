
def merge(a1, a2):
    a1.sort();
    a2.sort()
    merged = []
    i, j = 0, 0
    l1, l2 = len(a1), len(a2)
    while i < l1 and j < l2:
        if a1[i] < a2[j]:
            merged.append(a1[i])
            i += 1
        elif a1[i] > a2[j]:
            merged.append(a2[j])
            j += 1
        else:
            merged.append(a1[i])
            i += 1
            j += 1
    while i < l1:
        merged.append(a1[i])
        i += 1
    while j < l2:
        merged.append(a2[j])
        j += 1
    return merged



if __name__ == '__main__':
    print("Input two lists of integers to merge them:\n")
    a1 = [int(x) for x in input().split()]
    a2 = [int(x) for x in input().split()]
    merged = merge(a1, a2)
    print(' '.join([str(x) for x in merged]))