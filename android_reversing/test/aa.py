

def ans(inp):
    l = len(inp) - 1
    for i in range(len(inp)):
        start, end = i, l-i
        if inp[start] != inp[end]:
            print('0')
            return
    print('1')


def format(inp):
    pattern = '[a-zA-Z0-9]'
    inp = ''.join(filter(lambda x: re.match(pattern, x), inp))
    import re
    special_chars = ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '_', '=', '+', '{', '}', '[', ']', ':', ';', '"', "'", '<', '>', ',', '.', '?', '/', '\\']
    for char in special_chars:
        inp = inp.replace(char, '')
    return inp.lower().strip()

if __name__ == '__main__':
    inp = input()
    ans(format(inp))