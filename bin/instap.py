#!/usr/bin/env python3
#encoding: utf-8
# -*- coding: utf-8 -*-


if __name__ == '__main__':
    import sys
    import os

    testsdir = os.path.dirname(os.path.realpath(__file__))
    libdir = os.path.join(os.path.dirname(testsdir), "instaporter")
    sys.path.insert(0, os.path.join(os.path.dirname(testsdir)))

    from instaporter.instaporter import main

    main()
