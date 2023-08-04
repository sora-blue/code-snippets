import argparse
import json
import numpy as np
import pyperclip

def generate_random_array(dimensions, size, low, high):
    if len(size) == 1:
        size = [size[0] for _ in range(dimensions)]
    else:
        assert(len(size) == dimensions)
    shape = tuple(size[idx] for idx in range(dimensions))
    print(shape)
    array = np.random.randint(low, high, shape)
    return array

def main():
    parser = argparse.ArgumentParser(description='Generate random array and copy to clipboard')
    parser.add_argument('--dimensions', type=int, help='number of dimensions')
    parser.add_argument('--size', type=int, nargs='+', help='size of each dimension')
    parser.add_argument('--low', type=int, default=0, help='lower bound for random values')
    parser.add_argument('--high', type=int, default=10, help='upper bound for random values (not included)')

    args = parser.parse_args()

    array = generate_random_array(args.dimensions, args.size, args.low, args.high)
    array_list = array.tolist()
    array_str = json.dumps(array_list)

    pyperclip.copy(array_str)
    print('Random array copied to clipboard:\n', array_str)

if __name__ == '__main__':
    main()
