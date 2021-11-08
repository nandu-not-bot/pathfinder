from pprint import pprint
import random

matrix = [[0 for _ in range(9)] for _ in range(9)]


def make_maze(matrix, tall_seg=False):
    if len(matrix) <= 2 or len(matrix[0]) <= 2:
        return matrix


    m1 = []
    m2 = []

    if not tall_seg:
        mid = random.randint(1, len(matrix[0]) - 2 if len(matrix[0]) > 2 else 0)
        gap = random.randint(mid, len(matrix) - 2 if len(matrix) > 2 else 0)

        for y, row in enumerate(matrix):
            m1.append(row[:mid])
            m2.append(row[mid + 1:])
            for x, node in enumerate(row):
                if x == mid and y <= gap:
                    matrix[y][x] = 1

        m1 = make_maze(m1, True)
        m2 = make_maze(m2, True)

        ret = [
            m1[row] + [0 if row >= gap else 1] + m2[row]
            for row in range(len(m1))
        ]

        return ret

    else:
        mid = random.randint(1, len(matrix) - 2 if len(matrix) > 2 else 0)
        gap = random.randint(mid, len(matrix[0]) - 2 if len(matrix[0]) > 2 else 0)
        matrix[mid] = [(0 if x >= gap else 1) for x in range(len(matrix[0]))]
        
        m1 = make_maze(matrix[:mid])
        m2 = make_maze(matrix[mid + 1:])

        return m1 + [matrix[mid]] + m2

maze = make_maze(matrix)

for row in maze:
    for i in row:
        if i == 0:
            print("⬜ ", end="")
        elif i == 1:
            print("⬛ ", end="")

    print("\n")
