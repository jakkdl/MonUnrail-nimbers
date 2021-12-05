#!/usr/bin/python3

import argparse
import os
import pickle
from functools import cmp_to_key
import signal
import sys

results = {
    tuple(): 0
}
#untransformed_results = {
#    tuple(): 0
#}
optimal_moves = {
    tuple(): []
}

sigint = False

def complex_compare(x):
    return x.real,x.imag

def smaller(x, y):
    for a,b in zip(x, y):
        if a.real < b.real or (a.real == b.real and a.imag < b.imag):
            return -1
        if a.real > b.real or (a.real == b.real and a.imag > b.imag):
            return 1
    return 0

def rail_compare(a, b):
    if len(a) != len(b):
        return len(a) - len(b)
    return smaller(a, b)


def transform(rail):

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
        if smaller(t, smallest) < 0:
            smallest = t

    return smallest


class Transform:
    def __init__(self, origo, prim_delta, sec_delta, prim_len, sec_len):
        self.origo = origo
        self.prim_delta = prim_delta
        self.sec_delta = sec_delta
        self.prim_len = prim_len
        self.sec_len = sec_len

    def get_point(self, prim_steps, sec_steps):
        return (self.origo
                + self.prim_delta * prim_steps
                + self.sec_delta * sec_steps)

    def untransform(self, prim_steps, sec_steps):
        return (self.origo
                + self.prim_delta * prim_steps
                + self.sec_delta * sec_steps)



def transform3(rail):
    #def smaller(left, right):
    #    for sec in range(max(left.sec_len, right.sec_len)):
    #        for pri in range(max(left.prim_len, right.prim_len)):
    #            left_point = left.get_point(pri, sec)
    #            right_point = right.get_point(pri, sec)
    #            if left_point in rail and right_point not in rail:
    #                return True
    #            if left_point not in rail and right_point in rail:
    #                return False
    #    return False

    # idk I think this does the same thing as the one above... I'm tired
    def smaller(left, right):
        maxdim = max(realmax, imagmax)
        for real in range(maxdim):
            for imag in range(maxdim):
                if left.get_point(real, imag) in rail:
                    if not right.get_point(real, imag) in rail:
                        return True
                else:
                    if right.get_point(real, imag) in rail:
                        return False
        return False

    def apply_transform(transform, old_prim_len):
        ## both of these are broken
        #return [transform.untransform(p.real, p.imag) for p in rail]
        res = []
        if transform.prim_len == old_prim_len:
            for p in rail:
                res.append(complex(
                    abs(transform.origo.real - p.real),
                    abs(transform.origo.imag - p.imag)))
        else:
            for p in rail:
                res.append(complex(
                    abs(transform.origo.real - p.real),
                    abs(transform.origo.imag - p.imag)))
        return res


    realmax = 0
    imagmax = 0
    for point in rail:
        if point.real > realmax:
            realmax = int(point.real)
        if point.imag > imagmax:
            imagmax = int(point.imag)

    # define the transforms, as where their new origo will be
    # and along what axis - and in what direction, their new
    # primary axis would be.
    transforms = [
        Transform(complex( 0, 0),
                  complex( 1, 0), complex( 0, 1), realmax, imagmax),
        Transform(complex( 0, 0),
                  complex( 0, 1), complex( 1, 0), imagmax, realmax),

        Transform(complex( 0, imagmax),
                  complex( 1, 0), complex( 0,-1), realmax, imagmax),
        Transform(complex( 0, imagmax),
                  complex( 0,-1), complex( 1, 0), imagmax, realmax),

        Transform(complex(realmax, 0),
                  complex(-1, 0), complex( 0, 1), realmax, imagmax),
        Transform(complex(realmax,0),
                  complex( 0, 1), complex(-1, 0), imagmax, realmax),

        Transform(complex(realmax, imagmax),
                  complex(-1, 0), complex( 0,-1), realmax, imagmax),
        Transform(complex(realmax, imagmax),
                  complex( 0,-1), complex(-1, 0), imagmax, realmax),
    ]

    smallest = transforms[0]
    for transform in transforms[1:]:
        if smaller(transform, smallest):
            smallest = transform

    return sorted(apply_transform(transform, realmax), key=complex_compare)


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
                                  complex(row,col+1),
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


def write_to_human_readable(filename='monunrail.db'):
    def prettypoint(c):
        return f'{int(c.real)},{int(c.imag)}'
    def readable(rail):

        if isinstance(rail, complex):
            return prettypoint(rail)


        return ' '.join([f'{int(p.real)},{int(p.imag)}' for p in rail])

    keys = results.keys()
    sorted_keys = sorted(keys, key=cmp_to_key(rail_compare))
    with open(filename, 'w') as f:
        for key in sorted_keys:
            if key in optimal_moves:
                sorted_removes = sorted(optimal_moves[key])
                pretty_removes = ' - '.join([
                    f'{k}: {readable(optimal_moves[key][k])}'
                    for k in sorted_removes])
            else:
                pretty_removes = ''
            f.write(f'{readable(key)};\t{results[key]}\t' + pretty_removes + '\n')


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

#if __name__ == '__main__':
#    print(transform3([0+0j, 1+0j, 2+0j]))
#    print(transform3([0+0j, 0+1j, 0+2j]))

previous_games = [
    (
        0+0j,
        0+1j,
        0+2j,
        0+3j,
        1+0j,
        1+1j,
        1+2j,
        1+3j,
        2+2j,
        2+3j,
        2+4j,
        3+2j,
        3+3j,
        3+4j
    ),
    (
        0+0j,
        0+1j,
        0+2j,
        0+3j,
        0+4j,
        0+5j,
        1+0j,
        1+1j,
        1+2j,
        1+5j,
        2+2j,
        2+3j,
        2+4j,
        2+5j,
        3+0j,
        3+1j,
        3+2j,
        3+3j,
        3+4j,
        3+5j,
        4+0j,
        4+1j,
        4+2j,
        4+3j,
        4+4j,
    ),
    (
        0+0j,
        0+1j,
        0+2j,
        0+3j,
        0+4j,
        1+0j,
        1+1j,
        1+2j,
        1+3j,
        1+4j,
        2+0j,
        2+1j,
        2+2j,
        2+3j,
        3+1j,
        3+2j,
        4+1j,
        4+2j,
    ),
    (
        0+0j,
        0+1j,
        0+2j,
        0+3j,
        0+4j,
        1+0j,
        1+1j,
        1+2j,
        1+3j,
        1+4j,
        1+5j,
        2+4j,
        2+5j,
        3+4j,
        3+5j,
        4+4j,
        4+5j,
    ),
    (
        0+0j,
        0+1j,
        0+2j,
        0+3j,
        0+4j,
        1+0j,
        1+1j,
        1+2j,
        1+3j,
        1+4j,
        1+5j,
        2+0j,
        2+1j,
        2+2j,
        2+3j,
        2+4j,
        2+5j,
        3+0j,
        3+1j,
        3+2j,
        3+3j,
    ),
    (
        0+0j,
        0+1j,
        0+2j,
        0+3j,
        1+0j,
        1+1j,
        1+2j,
        1+3j,
        1+4j,
        2+0j,
        2+1j,
        2+2j,
        2+3j,
        2+4j,
        3+1j,
        3+2j,
        3+3j,
        4+2j,
        4+3j,
    ),
    (
        0+0j,
        0+1j,
        0+2j,
        0+3j,
        0+4j,
        1+0j,
        1+1j,
        1+2j,
        1+3j,
        1+4j,
        1+5j,
        2+1j,
        2+3j,
        2+4j,
        2+5j,
        3+1j,
        3+2j,
        3+3j,
        3+4j,
        3+5j,
    ),
]


def anki_write(res, maxlen=7):
    k = sorted(res.keys(), key=cmp_to_key(rail_compare))
    i = 0

    for rail in k:
        if len(rail) < 7:
            continue
        if len(rail) > maxlen:
            break
        i += 1
        print(i)
        xmax = 0
        ymax = 0
        for p in rail:
            if p.real > xmax:
                xmax = int(p.real)
            if p.imag > ymax:
                ymax = int(p.imag)

        for x in range(xmax+1):
            for y in range(ymax+1):
                if complex(x, y) in rail:
                    print('X', end='')
                else:
                    print(' ', end='')
            print()
        print(res[rail])
        print()








def signal_handler(sig, frame):
    print('caught sigint, aborting and writing to file')
    if dump_on_sigint == True:
        pickledump('results.pickle', results)
        pickledump('optimal_moves.pickle', optimal_moves)
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

dump_on_sigint = False

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='ALL THE NIMBERS')
    parser.add_argument('rows', type=int)
    parser.add_argument('cols', type=int)
    parser.add_argument('--printres', action='store_true')
    parser.add_argument('--noload', action='store_true')
    parser.add_argument('--nodump', action='store_true')
    parser.add_argument('--export', action='store_true')
    parser.add_argument('--generate-previous', action='store_true')
    parser.add_argument('--print-anki', action='store_true')

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

    if not args['nodump']:
        dump_on_sigint = True
    k = generate_block(args['rows'], args['cols'])
    print(nimber(k))
    #print(len(untransformed_results))

    if args['print_anki']:
        anki_write(results)

    if args['generate_previous']:
        previous_games.sort(key=len)
        for rail in previous_games:
            print(f'len: {len(rail)}')
            input()
            print(nimber(rail))
            print(rail in results)
    print(len(results))

    if args['printres']:
        import pprint
        pprint.pprint(results)


    if not args['nodump']:
        print('dumping...')
        pickledump('results.pickle', results)
        pickledump('optimal_moves.pickle', optimal_moves)
        #pickledump('untransformed_results.pickle', untransformed_results)

    if args['export']:
        print('exporting...')
        write_to_human_readable()




