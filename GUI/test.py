# -*- coding: utf-8 -*-

import os
import sys
import argparse


import test.test_animation_qt as qt
import test.test_animation_matplotlib as mat


def main(argv):
    parser = argparse.ArgumentParser()

    parser.add_argument("-m", "--mat", help="test Matplotlib viewer",
                        action="store_true")
    parser.add_argument("-v", "--vna", help="test PicoVNA",
                        action="store_true")
    args = parser.parse_args()

    if args.mat:
        print("Activiate Matplotlib Viewer")
        mat.main(sys.argv)

    elif args.vna:
        print("Activiate Matplotlib Viewer")
        vna.main(sys.argv)

    else:
        parser.print_help(sys.stderr)


if __name__ == '__main__':
    main(sys.argv)
    sys.exit()
