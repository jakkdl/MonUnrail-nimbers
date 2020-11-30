#!/usr/bin/python3

import os
import pickle

results = {
    tuple(): 0
}
optimal_moves = {
    tuple(): []
}

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __lt__(self, other):
        return self.x < other.x or (self.x == other.x and self.y < other.y)

    def __add__(self, other):
        return Point(self.x+other.x, self.y+other.y)

    def __sub__(self, other):
        return Point(self.x-other.x, self.y-other.y)

    def __mul__(self, scalar):
        return Point(self.x*scalar, self.y*scalar)

    def __str__(self):
        return f'({self.x}, {self.y})'

    def __repr__(self):
        return f'({self.x}, {self.y})'

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return tuple((self.x, self.y)).__hash__()


def complex_compare(x):
    return x
    #return x.real,x.imag

def transform(rail):
    def smaller(x, y):
        for a,b in zip(x, y):
            if complex_compare(a) < complex_compare(b):
                return True
            if complex_compare(a) > complex_compare(b):
                return False
        return False

    transforms = (
        lambda x: Point(x.x, -x.y),
        lambda x: Point(-x.x, x.y),
        lambda x: Point(-x.x, -x.y),
        lambda x: Point(x.y, x.x),
        lambda x: Point(x.y, -x.x),
        lambda x: Point(-x.y, x.x),
        lambda x: Point(-x.y, -x.x),
    )

    transformed_rails = [[]*7]
    for point in rail:
        for transformed_rail, transform_f in zip(transformed_rails,
                                                 transforms):
            transformed_rail.append(transform_f(point))

    transformed_rails = [
        shift_to_origo(
            sorted(t, key=complex_compare)
        ) for t in transformed_rails
    ]

    smallest = rail
    for t in transformed_rails:
        if smaller(t, smallest):
            smallest = t

    return smallest

def shift_to_origo(rail):
    min_x = None
    min_y = None
    for piece in rail:
        if min_x == None or piece.x < min_x:
            min_x = piece.x
        if min_y == None or piece.y < min_y:
            min_y = piece.y

    return tuple(point-Point(min_x, min_y) for point in rail)

def smallest_nimber_not_in(nimbers):
    i = 0
    while i in nimbers:
        i += 1
    return i

def split(rail):
    split_rails = []
    remaining = set(rail)

    while remaining:
        split_rails.append({remaining.pop()})

        while True:
            added = []
            for rem in remaining:
                for offset in (Point(0,1), Point(1,0),
                               Point(0, -1), Point(-1, 0)):
                    if offset+rem in split_rails[-1]:
                        added.append(rem)
                        break
            if not added:
                break

            for add in added:
                remaining.remove(add)
                split_rails[-1].add(add)


    res = [tuple(sorted(split, key=complex_compare)) for split in split_rails]

    return res


# removal
def nimber(rail):
    # generate all mirrors & rotations (offset towards zero!)
    # sort each transform individually
    # take the smallest transform

    #rail = shift_to_origo(rail)
    rail = transform(rail)

    # check if we already have a nimber
    #print(rail)
    if rail in results:
        return results[rail]




    # try every possible removal, get the nimber for each one

    # calculate max rows and cols
    rows=0
    cols=0
    for coord in rail:
        if coord.x > rows:
            rows = coord.x
        if coord.y > cols:
            cols = coord.y

    global_nimbers = set()

    for row in range(rows+1):
        for col in range(cols+1):
            if Point(row,col) not in rail:
                continue

            for mod in (Point(0,1), Point(1,0)):
                for num in (1,2,3):
                    # ugly optimization to not double check single removal
                    if mod == Point(1,0) and num==1:
                        continue

                    remove = [Point(row,col) + mod*i for i in range(num)]
                    valid = True

                    for r in remove:
                        if r not in rail:
                            valid = False
                            break
                    if not valid:
                        break

                    curr_rail = rail
                    for r in remove:
                        index = curr_rail.index(r)
                        curr_rail = curr_rail[:index] + curr_rail[index+1:]



                    split_rails = split(curr_rail)

                    local_nimber = 0
                    for split_rail in split_rails:
                        n = nimber(split_rail)
                        local_nimber ^= n

                    if local_nimber == 0 and rail not in optimal_moves:
                        optimal_moves[rail] = remove

                    global_nimbers.add(local_nimber)


    res = smallest_nimber_not_in(global_nimbers)

    results[rail] = res
    #print(res, rail)

    return res





if __name__ == '__main__':
    #if os.path.isfile('results.pickle'):
    #    with open('results.pickle', 'rb') as f:
    #        results = pickle.load(f)
    #if os.path.isfile('optimal_moves.pickle'):
    #    with open('optimal_moves.pickle', 'rb') as f:
    #        optimal_moves = pickle.load(f)

    #print( nimber(((0,0),(0,1)) ))
    #print( split(((0,0),(0,1),(2,2)) ))

    k = tuple(Point(x,y) for x in range(4) for y in range(4))
    print(nimber(k))
    print(len(results))
    #import pprint
    #pprint.pprint(results)

    #with open('results.pickle', 'wb') as f:
    #    pickle.dump(results, f)
    #with open('optimal_moves.pickle', 'wb') as f:
    #    pickle.dump(optimal_moves, f)




