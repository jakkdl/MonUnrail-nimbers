#!/usr/bin/python3

import argparse
import os
import pickle

results = {
    tuple(): 0
}
#untransformed_results = {
#    tuple(): 0
#}
optimal_moves = {
    tuple(): []
}

def complex_compare(x):
    return x.real,x.imag

def transform(rail):
    def smaller(x, y):
        for a,b in zip(x, y):
            if a.real < b.real or (a.real == b.real and a.imag < b.imag):
                return True
            if a.real > b.real or (a.real == b.real and a.imag > b.imag):
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

    transformed_rails.append(rail)

    transformed_rails = [
        shift_to_origo(
            sorted(t, key=complex_compare)
        ) for t in transformed_rails
    ]

    smallest = transformed_rails[0]
    for t in transformed_rails[1:]:
        if smaller(t, smallest):
            smallest = t

    return smallest


class Transform:
    def __init__(self, origo, prim_delta, sec_delta, prim_len, sec_len):
        self.origo = origo
        self.prim_delta = delta
        self.sec_delta = delta
        self.prim_len = prim_len
        self.sec_len = sec_len

    def get_point(prim_steps, sec_steps):
        return (self.origo
                + self.prim_delta * prim_steps
                + self.sec_delta * sec_steps)


def transform3(rail):
    def smaller(left, right):
        for sec in range(max(left.secondary_size, left.secondary_size)):
            for pri in range(max(right.primary_size, right.primary_size)):
                left_point = left.get_point(pri, sec)
                right_point = right.get_point(pri, sec)
                if left_point in rail and right_point not in rail:
                    return True
                if left_point not in rail and right_point in rail:
                    return False

    realmax = 0
    imagmax = 0
    for point in rail:
        if point.real > realmax:
            realmax = point.real
        if point.imag > imagmax:
            imagmax = point.imag

    # define the transforms, as where their new origo will be
    # and along what axis - and in what direction, their new
    # primary axis would be.
    transforms = [
        Transform(complex(0,0),
                  complex(1,0), complex(0,1), realmax, imagmax),
        Transform(complex(0,0),
                  complex(0,1), complex(1,0), imagmax, realmax),

        Transform(complex(0,imagmax),
                  complex(1,0), complex(0,-1), realmax, imagmax),
        Transform(complex(0,imagmax),
                  complex(0,-1), complex(1,0), imagmax, realmax),

        Transform(complex(realmax, 0),
                  complex(-1,0), complex(0,1), realmax, imagmax),
        Transform(complex(realmax,0),
                  complex(0,1), complex(-1,0), imagmax, realmax),

        Transform(complex(realmax,imagmax),
                  complex(-1,0), complex(0,-1), realmax, imagmax),
        Transform(complex(realmax,imagmax),
                  complex(0,-1), complex(-1,0), imagmax, realmax),
    ]

    smallest = transforms[0]
    for transform in transforms:
        if smaller(smallest, transform):
            smallest = transform

    return apply_transform(transform)


    #transforms = []
    #for origo_x,delta_x in zip((0, realmax), (complex(0,1),complex(0,-1))):
    #    for origo_y,delta_y in zip((0, imagmax), complex(1,0),complex(-1,0)):
    #        transforms.append(
    #            Transform(complex(origo_x, origo_y), delta_x, delta_y, realmax, imagmax)
    #        )
    #        transforms.append(
    #            Transform(complex(origo_x, origo_y), delta_y, delta_x, imagmax, realmax)
    #        )



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


def split(rail):
    split_rails = []
    remaining = set(rail)

    while remaining:
        split_rails.append([])
        unchecked_points = [remaining.pop()]
        while unchecked_points and remaining:
            check = unchecked_points.pop()
            for offset in (complex(0,1),
                           complex(1,0),
                           complex(0, -1),
                           complex(-1, 0)
                          ):
                k = check+offset
                if k in remaining:
                    unchecked_points.append(k)
                    remaining.remove(k)
            split_rails[-1].append(check)
        if unchecked_points:
            split_rails[-1].extend(unchecked_points)

    #res = [tuple(sorted(split, key=complex_compare)) for split in split_rails]
    res = [tuple(split) for split in split_rails]
    return res
    #return [tuple(r) for r in split_rails]



mods = (
    (),
    (complex(0,1),),
    (complex(0,1),complex(0,2),),
    (complex(1,0),),
    (complex(1,0),complex(2,0),),
)


# removal
def nimber(ograil):
    # generate all mirrors & rotations (offset towards zero!)
    # sort each transform individually
    # take the smallest transform

    #if ograil in untransformed_results:
        #return untransformed_results[ograil]
    if ograil in results:
        return results[ograil]

    #rail = shift_to_origo(rail)
    rail = transform(ograil)

    # check if we already have a nimber
    #print(rail)
    if rail in results:
        res = results[rail]
        #if ograil not in untransformed_results:
            #untransformed_results[ograil] = res
        return res



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



    res = smallest_nimber_not_in(global_nimbers)

    results[rail] = res
    #print(res, rail)

    return res


def do_stuff(rail, curr_rail, remove):
    split_rails = split(curr_rail)
    #if split_rails != split2(curr_rail):
        #print(curr_rail)

    local_nimber = 0
    for split_rail in split_rails:
        n = nimber(split_rail)
        local_nimber ^= n

    if rail not in optimal_moves:
        optimal_moves[rail] = {local_nimber: remove}
    elif local_nimber not in optimal_moves[rail]:
        optimal_moves[rail][local_nimber] = remove
    return local_nimber

def pickleload(filename):
    if os.path.isfile(filename):
        with open(filename, 'rb') as f:
            return pickle.load(f)

def pickledump(filename, data):
    with open(filename, 'wb') as f:
        pickle.dump(data, f)

def generate_block(rows, cols):
    return tuple(complex(x,y) for x in range(rows)
              for y in range(cols))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='ALL THE NIMBERS')
    parser.add_argument('rows', type=int)
    parser.add_argument('cols', type=int)
    parser.add_argument('--printres', action='store_true')
    parser.add_argument('--noload', action='store_true')
    parser.add_argument('--nodump', action='store_true')
    args = vars(parser.parse_args())

    if not args['noload']:
        results = pickleload('results.pickle')
        optimal_moves = pickleload('optimal_moves.pickle')
        #untransformed_results = pickleload('untransformed_results.pickle')
        #if os.path.isfile('results.pickle'):
        #    with open('results.pickle', 'rb') as f:
        #        results = pickle.load(f)
        #if os.path.isfile('optimal_moves.pickle'):
        #    with open('optimal_moves.pickle', 'rb') as f:
        #        optimal_moves = pickle.load(f)

    #k = tuple(complex(x,y) for x in range(args['rows'])
    #          for y in range(args['cols']))
    k = generate_block(args['rows'], args['cols'])
    print(nimber(k))
    print(len(results))
    #print(len(untransformed_results))
    if args['printres']:
        import pprint
        pprint.pprint(results)

    if not args['nodump']:
        pickledump('results.pickle', results)
        pickledump('optimal_moves.pickle', optimal_moves)
        #pickledump('untransformed_results.pickle', untransformed_results)




