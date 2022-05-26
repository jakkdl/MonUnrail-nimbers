#!/usr/bin/python3
"""Program for calculating nimbers of shapes in the game MonUnrail"""

import argparse
import os
import pickle
from functools import cmp_to_key
import signal
import sys

from typing import Union, Iterable, Any, Callable, Optional
from types import FrameType

from previous_games import previous_games

Rail = tuple[complex, ...]
Move = Union[tuple[complex], tuple[complex,complex], tuple[complex, complex, complex]]
Nimber = int
Results = dict[Rail, Nimber]
OptimalMoves = Optional[dict[Rail, dict[Nimber, Move]]]


def complex_to_tuple(number: complex) -> tuple[int, int]:
    """Since complex.__lt__ doesn't work with other complex numbers, treat it
    as a tuple and sort primarily on the real"""
    return number.real,number.imag #type: ignore

def smaller(left_shape: Rail, right_shape: Rail) -> int:
    """Compare two rails, use 'rail_compare' if they are not the same size"""
    for left_tile,right_tile in zip(left_shape, right_shape):
        if complex_to_tuple(left_tile) < complex_to_tuple(right_tile):
            return -1
        if complex_to_tuple(left_tile) > complex_to_tuple(right_tile):
            return 1
    return 0

def rail_compare(lhs: Rail, rhs: Rail) -> int:
    """Compare two rails two find the "smaller" one"""
    if len(lhs) != len(rhs):
        return len(lhs) - len(rhs)
    return smaller(lhs, rhs)


def transform(rail: Rail) -> Rail:
    """rotate/move a rail to it's smallest transform"""

    # type hinting lambdas is a pain / barely a thing
    transforms: tuple[Callable[[complex],complex]] = ( #type: ignore
        lambda x: complex(x.real, -x.imag),
        lambda x: complex(-x.real, x.imag),
        lambda x: complex(-x.real, -x.imag),
        lambda x: complex(x.imag, x.real),
        lambda x: complex(x.imag, -x.real),
        lambda x: complex(-x.imag, x.real),
        lambda x: complex(-x.imag, -x.real),
    )

    transformed_rails: list[Rail] = [
            tuple(transform_f(point) for point in rail)
            for transform_f in transforms
            ] + [rail]

    transformed_rails = [
        shift_to_origo(
            sorted(t, key=complex_to_tuple)
        ) for t in transformed_rails
    ]

    smallest = transformed_rails[0]
    for t_rail in transformed_rails[1:]:
        if smaller(t_rail, smallest) < 0:
            smallest = t_rail

    return smallest


#class Transform:
#    def __init__(self, origo, prim_delta, sec_delta, prim_len, sec_len):
#        self.origo = origo
#        self.prim_delta = prim_delta
#        self.sec_delta = sec_delta
#        self.prim_len = prim_len
#        self.sec_len = sec_len
#
#    def get_point(self, prim_steps, sec_steps):
#        return (self.origo
#                + self.prim_delta * prim_steps
#                + self.sec_delta * sec_steps)
#
#    def untransform(self, prim_steps, sec_steps):
#        return (self.origo
#                + self.prim_delta * prim_steps
#                + self.sec_delta * sec_steps)



#def transform3(rail):
#    #def smaller(left, right):
#    #    for sec in range(max(left.sec_len, right.sec_len)):
#    #        for pri in range(max(left.prim_len, right.prim_len)):
#    #            left_point = left.get_point(pri, sec)
#    #            right_point = right.get_point(pri, sec)
#    #            if left_point in rail and right_point not in rail:
#    #                return True
#    #            if left_point not in rail and right_point in rail:
#    #                return False
#    #    return False
#
#    # idk I think this does the same thing as the one above... I'm tired
#    def smaller(left, right):
#        maxdim = max(realmax, imagmax)
#        for real in range(maxdim):
#            for imag in range(maxdim):
#                if left.get_point(real, imag) in rail:
#                    if not right.get_point(real, imag) in rail:
#                        return True
#                else:
#                    if right.get_point(real, imag) in rail:
#                        return False
#        return False
#
#    def apply_transform(transform, old_prim_len):
#        ## both of these are broken
#        #return [transform.untransform(p.real, p.imag) for p in rail]
#        res = []
#        if transform.prim_len == old_prim_len:
#            for p in rail:
#                res.append(complex(
#                    abs(transform.origo.real - p.real),
#                    abs(transform.origo.imag - p.imag)))
#        else:
#            for p in rail:
#                res.append(complex(
#                    abs(transform.origo.real - p.real),
#                    abs(transform.origo.imag - p.imag)))
#        return res
#
#
#    realmax = 0
#    imagmax = 0
#    for point in rail:
#        if point.real > realmax:
#            realmax = int(point.real)
#        if point.imag > imagmax:
#            imagmax = int(point.imag)
#
#    # define the transforms, as where their new origo will be
#    # and along what axis - and in what direction, their new
#    # primary axis would be.
#    transforms = [
#        Transform(complex( 0, 0),
#                  complex( 1, 0), complex( 0, 1), realmax, imagmax),
#        Transform(complex( 0, 0),
#                  complex( 0, 1), complex( 1, 0), imagmax, realmax),
#
#        Transform(complex( 0, imagmax),
#                  complex( 1, 0), complex( 0,-1), realmax, imagmax),
#        Transform(complex( 0, imagmax),
#                  complex( 0,-1), complex( 1, 0), imagmax, realmax),
#
#        Transform(complex(realmax, 0),
#                  complex(-1, 0), complex( 0, 1), realmax, imagmax),
#        Transform(complex(realmax,0),
#                  complex( 0, 1), complex(-1, 0), imagmax, realmax),
#
#        Transform(complex(realmax, imagmax),
#                  complex(-1, 0), complex( 0,-1), realmax, imagmax),
#        Transform(complex(realmax, imagmax),
#                  complex( 0,-1), complex(-1, 0), imagmax, realmax),
#    ]
#
#    smallest = transforms[0]
#    for transform in transforms[1:]:
#        if smaller(transform, smallest):
#            smallest = transform
#
#    return sorted(apply_transform(transform, realmax), key=complex_to_tuple)
#
#
#    #transforms = []
#    #for origo_x,delta_x in zip((0, realmax), (complex(0,1),complex(0,-1))):
#    #    for origo_y,delta_y in zip((0, imagmax), complex(1,0),complex(-1,0)):
#    #        transforms.append(
#    #            Transform(complex(origo_x, origo_y), delta_x, delta_y, realmax, imagmax)
#    #        )
#    #        transforms.append(
#    #            Transform(complex(origo_x, origo_y), delta_y, delta_x, imagmax, realmax)
#    #        )



def shift_to_origo(rail: Rail | list[complex]) -> Rail:
    """Shift a rail towards origo by calculating it's min_x and min_y"""
    min_x = rail[0].real
    min_y = rail[0].imag
    for piece in rail[1:]:
        if piece.real < min_x:
            min_x = piece.real
        if piece.imag < min_y:
            min_y = piece.imag

    return tuple(point-complex(min_x, min_y) for point in rail)

def smallest_nimber_not_in(nimbers: Iterable[Nimber]) -> Nimber:
    """return the smallest nimber not in a list"""
    i = 0
    while i in nimbers:
        i += 1
    return i


def split(rail: Rail) -> list[Rail]:
    """check if a rail is in fact two disparate pieces, in which case
    return it as two separate rails"""
    split_rails: list[list[complex]] = []
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
def nimber(ograil: Rail, results: Results, optimal_moves: OptimalMoves,
        all_zeros = False) -> int:
    """Calculate the nimber of a rail"""
    def do_stuff(rail: Rail, curr_rail: Rail, remove: Move) -> Nimber:
        """rail is the shape we're calculating the nimber for,
        curr_rail is the shape that's left after removing the pieces in remove

        returns the nimber of curr_rail
        """
        split_rails = split(curr_rail)

        local_nimber = 0
        for split_rail in split_rails:
            local_nimber ^= nimber(split_rail, results, optimal_moves)

        if all_zeros and local_nimber == 0:
            print(remove)

        if optimal_moves is not None:
            if rail not in optimal_moves:
                optimal_moves[rail] = {local_nimber: remove}
            elif local_nimber not in optimal_moves[rail]:
                optimal_moves[rail][local_nimber] = remove

        return local_nimber

    # generate all mirrors & rotations (offset towards zero!)
    # sort each transform individually
    # take the smallest transform

    # check if we already have a nimber
    if ograil in results:
        return results[ograil]

    rail = transform(ograil)
    if rail in results:
        res = results[rail]
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

            global_nimbers.add(do_stuff(rail, curr_rail, (complex(row,col),)))

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

    return res




def write_to_human_readable(results: Results,
        optimal_moves: OptimalMoves,
        filename: str ='monunrail.db') -> None:
    """Write the results to a human-readable text file"""
    def prettypoint(point: complex) -> str:
        return f'{int(point.real)},{int(point.imag)}'

    def readable(rail: Rail) -> str:
        if isinstance(rail, complex):
            return prettypoint(rail)

        return ' '.join([f'{int(p.real)},{int(p.imag)}' for p in rail])

    keys = results.keys()
    sorted_keys = sorted(keys, key=cmp_to_key(rail_compare))
    with open(filename, 'w', encoding='utf-8') as file:
        for key in sorted_keys:
            if optimal_moves and key in optimal_moves:
                sorted_removes = sorted(optimal_moves[key])
                pretty_removes = ' - '.join([
                    f'{k}: {readable(optimal_moves[key][k])}'
                    for k in sorted_removes])
            else:
                pretty_removes = ''
            file.write(f'{readable(key)};\t{results[key]}\t' + pretty_removes + '\n')


def pickledump(filename: str, data: Any) -> None:
    """dump data to a file with name filename"""
    with open(filename, 'wb') as file:
        pickle.dump(data, file)

def generate_block(rows: int, cols: int) -> Rail:
    """Generate a square rail of size rows*cols"""
    return tuple(complex(x,y) for x in range(rows)
              for y in range(cols))



def anki_write(res: dict[Rail, Nimber], maxlen: int=7) -> None:
    """Print shapes and nimbers in a format that's good for entering into anki"""
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
        for point in rail:
            if point.real > xmax:
                xmax = int(point.real)
            if point.imag > ymax:
                ymax = int(point.imag)

        for x_coord in range(xmax+1):
            for y_coord in range(ymax+1):
                if complex(x_coord, y_coord) in rail:
                    print('X', end='')
                else:
                    print(' ', end='')
            print()
        print(res[rail])
        print()

def signal_handler(_sig: int, frame: Optional[FrameType]) -> None:
    """Dump database before aborting"""
    print('caught sigint, aborting and writing to file')

    # Restore signal to default in case this code breaks
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    results : Results = {}
    optimal_moves : OptimalMoves = {}

    while frame and frame.f_locals:
        if 'results' in frame.f_locals:
            results = frame.f_locals['results']
        if 'optimal_moves' in frame.f_locals:
            optimal_moves = frame.f_locals['optimal_moves']
        if results and optimal_moves:
            break

        frame = frame.f_back

    if not results and not optimal_moves:
        print('found no results')
        sys.exit(0)

    for data, name in ((results, 'results'), (optimal_moves, 'optimal_moves')):
        if data:
            pickledump(f'{name}_dump.pickle', data)
            print(f'dumped {name} to pickle')

    sys.exit(0)



def main() -> None:
    """ALL THE NIMBERS"""
    signal.signal(signal.SIGINT, signal_handler)

    # We use a global variable to store results in to be able to dump
    # them on sigint
    # pylint: disable=global-statement

    parser = argparse.ArgumentParser(description='ALL THE NIMBERS')
    parser.add_argument('rows', type=int)
    parser.add_argument('cols', type=int)
    parser.add_argument('--printres', action='store_true')
    parser.add_argument('--noload', action='store_true')
    parser.add_argument('--nodump', action='store_true')
    parser.add_argument('--export', action='store_true')
    parser.add_argument('--optimal-moves', action='store_true')
    parser.add_argument('--generate-previous', action='store_true')
    parser.add_argument('--print-anki', action='store_true')

    args = vars(parser.parse_args())
    results: Results = { tuple(): 0 }

    optimal_moves: OptimalMoves = { tuple(): {} }

    if not args['noload']:
        print('loading.. ', end=' ', flush=True)
        if os.path.isfile('results.pickle'):
            with open('results.pickle', 'rb') as file:
                results = pickle.load(file)
        print('...', end=' ', flush=True)
        if os.path.isfile('optimal_moves.pickle'):
            with open('optimal_moves.pickle', 'rb') as file:
                optimal_moves = pickle.load(file)
        print('loaded data')

    results_len = len(results)

    if not args['optimal_moves']:
        optimal_moves = None


    k = generate_block(args['rows'], args['cols'])
    print(nimber(k, results, optimal_moves))

    if args['print_anki']:
        anki_write(results)

    if args['generate_previous']:
        previous_games.sort(key=len)
        for rail in previous_games:
            #print(f'len: {len(rail)}')
            print(nimber(rail, results, optimal_moves), end=', ', flush=True)
        print()
    print(len(results))

    if args['printres']:
        #pprint.pprint(results)
        print(', '.join(map(str, results.values())))

    if args['export']:
        print('exporting...')
        write_to_human_readable(results, optimal_moves)

    if args['nodump']:
        return
    if len(results) == results_len:
        print('no new data...')
        return
    print('dumping...')
    pickledump('results.pickle', results)
    if optimal_moves is not None:
        pickledump('optimal_moves.pickle', optimal_moves)


if __name__ == '__main__':
    main()
