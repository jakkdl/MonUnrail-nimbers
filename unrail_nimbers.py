#!/usr/bin/python3

import os
import pickle

results = {
    tuple(): 0
}
optimal_moves = {
    tuple(): []
}

def complex_compare(x):
    return x.real,x.imag

def transform(rail):
    def smaller(x, y):
        for a,b in zip(x, y):
            if complex_compare(a) < complex_compare(b):
            #if a.real < b.real or (a.real == b.real and a.imag < b.imag):
                return True
            if complex_compare(a) > complex_compare(b):
            #if a.real > b.real or (a.real == b.real and a.imag > b.imag):
                return False
        return False

    transforms = (
        lambda x: complex(x.real, -x.imag),
        lambda x: complex(-x.real, x.imag),
        lambda x: complex(-x.real, -x.imag),
        lambda x: complex(x.imag, x.real),
        lambda x: complex(x.imag, -x.real),
        lambda x: complex(-x.imag, x.real),
        lambda x: complex(-x.imag, -x.real),
    )

    transformed_rails = [[],[],[],[],[],[],[]]
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
        if min_x == None or piece.real < min_x:
            min_x = piece.real
        if min_y == None or piece.imag < min_y:
            min_y = piece.imag

    return tuple(point-complex(min_x, min_y) for point in rail)

def smallest_nimber_not_in(nimbers):
    i = 0
    while i in nimbers:
        i += 1
    return i


#TODO optimize
def split(rail):
    split_rails = []
    remaining = set(rail)

    while remaining:
        split_rails.append({remaining.pop()})

        while True:
            added = []
            for rem in remaining:
                for offset in (complex(0,1), complex(1,0),
                               complex(0, -1), complex(-1, 0)):
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

mods = (
    (),
    (complex(0,1),),
    (complex(0,1),complex(0,2),),
    (complex(1,0),),
    (complex(1,0),complex(2,0),),
)


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
        if coord.real > rows:
            rows = int(coord.real)
        if coord.imag > cols:
            cols = int(coord.imag)

    global_nimbers = set()

    for row in range(rows+1):
        for col in range(cols+1):
            if complex(row,col) not in rail:
                continue

            index = rail.index(complex(row,col))
            curr_rail = rail[:index] + rail[index+1:]

            global_nimbers.add(do_stuff(rail, curr_rail, complex(row,col)))

            if complex(row+1, col) in curr_rail:
                index = curr_rail.index(complex(row+1,col))
                row_rail = curr_rail[:index] + curr_rail[index+1:]

                global_nimbers.add(do_stuff(rail, row_rail,
                                            (complex(row,col),
                                             complex(row+1,col))))

                if complex(row+2, col) in row_rail:
                    index = row_rail.index(complex(row+2,col))
                    row_rail = row_rail[:index] + row_rail[index+1:]

                    global_nimbers.add(do_stuff(rail, row_rail,
                                                (complex(row,col),
                                                 complex(row+1,col),
                                                 complex(row+2,col))))
            if complex(row, col+1) in curr_rail:
                index = curr_rail.index(complex(row,col+1))
                curr_rail = curr_rail[:index] + curr_rail[index+1:]

                global_nimbers.add(
                    do_stuff(rail, curr_rail,
                             (complex(row,col),
                              complex(row,col+1))))

                if complex(row, col+2) in curr_rail:
                    index = curr_rail.index(complex(row,col+2))
                    curr_rail = curr_rail[:index] + curr_rail[index+1:]

                    global_nimbers.add(
                        do_stuff(rail, curr_rail,
                                 (complex(row,col),
                                  complex(row,col+2),
                                  complex(row,col+2))))



            #for mod in mods:

            #    remove = [complex(row,col) + m for m in mod]
            #    valid = True

            #    for r in remove:
            #        if r not in rail:
            #            valid = False
            #            break
            #    if not valid:
            #        continue

            #    curr_rail = list(rail)
            #    curr_rail.remove(complex(row,col))

            #    for r in remove:
            #        index = curr_rail.index(r)
            #        curr_rail = curr_rail[:index] + curr_rail[index+1:]

            #    do_stuff(rail, curr_rail, remove)





    res = smallest_nimber_not_in(global_nimbers)

    results[rail] = res
    #print(res, rail)

    return res


def do_stuff(rail, curr_rail, remove):
    split_rails = split(curr_rail)

    local_nimber = 0
    for split_rail in split_rails:
        n = nimber(split_rail)
        local_nimber ^= n

    if local_nimber == 0 and rail not in optimal_moves:
        optimal_moves[rail] = remove



if __name__ == '__main__':
    #if os.path.isfile('results.pickle'):
    #    with open('results.pickle', 'rb') as f:
    #        results = pickle.load(f)
    #if os.path.isfile('optimal_moves.pickle'):
    #    with open('optimal_moves.pickle', 'rb') as f:
    #        optimal_moves = pickle.load(f)

    #print( nimber(((0,0),(0,1)) ))
    #print( split(((0,0),(0,1),(2,2)) ))

    k = tuple(complex(x,y) for x in range(4) for y in range(4))
    print(nimber(k))
    print(len(results))
    #import pprint
    #pprint.pprint(results)

    with open('results.pickle', 'wb') as f:
        pickle.dump(results, f)
    with open('optimal_moves.pickle', 'wb') as f:
        pickle.dump(optimal_moves, f)




