#!/usr/bin/env python

"""
LAST.vc Anagram Solver

Author: Brendon Crawford <brendon@last.vc>
"""

import os
import sys
import re
import random
import multiprocessing as mp
from optparse import OptionParser


def main():
    """
    Main Routine from Command Line

    Returns: Int
    """
    options, _ = get_options()
    data, orig_data = get_input_data()
    if len(data) == 0:
        print("Invalid input data")
        return False
    else:
        wordlist, lenmap = get_wordlist()
        out = solver(options.workers, options.jobs, data, wordlist, lenmap)
        show_results(out, orig_data)
        return True


def get_options():
    """
    Get options
    """
    usage = 'Usage: echo "input phrase" | %prog [options]'
    parser = OptionParser(usage=usage)
    parser.add_option('-w', '--workers', type='int', dest='workers',
                      default=2, help="Workers per CPU")
    parser.add_option('-j', '--jobs', type='int', dest='jobs',
                      default=2, help="Jobs per worker")
    options, args = parser.parse_args()
    return (options, args)


def solver(workers, jobs, data, wordlist, lenmap):
    """
    Solver worker
    """
    p_count = workers * mp.cpu_count()
    j_count = p_count * jobs
    pool = mp.Pool(processes=p_count)
    results = [pool.apply_async(cycle_all, [data, wordlist, lenmap])
               for i in xrange(j_count)]
    resvals = [r.get() for r in results]
    bestchoice = reduce(lambda a, b: a if len(a) > len(b) else b, resvals)
    return bestchoice


def get_score(out, orig_data):
    """
    Gets score string
    """
    score = "%0.2f%%" % ((float(len(out)) / float(len(orig_data))) * 100)
    return score


def show_results(out, orig_data):
    """
    Shows Results
    """
    print
    print("Subject:\n%s\n" % orig_data)
    print("Anagram:\n%s\n" % out)
    print("Score:\n%s" % get_score(out, orig_data))
    print
    return True


def get_input_data():
    """
    Get input data
    """
    orig_data = sys.stdin.read().strip()
    data = re.sub(r'[^a-zA-Z]', '', orig_data)
    return (data, orig_data)


def get_wordlist():
    """
    Gets wordlist
    """
    dname = os.path.dirname(__file__)
    fname = os.path.realpath(dname + '/data/wordlist.txt')
    fh = open(fname, 'r')
    wordlist = frozenset([x.rstrip() for x in fh])
    fh.close()
    lenmap = {}
    for word in wordlist:
        wordlen = len(word)
        if wordlen not in lenmap:
            lenmap[wordlen] = []
        lenmap[wordlen].append(word)
    return (wordlist, lenmap)


def cycle_all(data, wordlist, lenmap):
    """
    Cycle
    """
    found_words = []
    bucket = ''
    word = data
    while len(word) > 0:
        found_word = find_match(word, wordlist, lenmap)
        if found_word is None:
            word, extra = extract_word(word)
            bucket += extra
        else:
            found_words.append(found_word)
            word = bucket
            bucket = ''
    out = build_output(found_words)
    return out


def build_output(found_words):
    """
    Builds output string
    """
    random.shuffle(found_words)
    out = ' '.join(found_words)
    return out


def find_match(word, wordlist, lenmap):
    """
    Find a match of word against wordlist
    """
    wordlen = len(word)
    sword = sorted(word)
    if wordlen in lenmap:
        for target_word in lenmap[wordlen]:
            ismatch = (sword == sorted(target_word))
            if ismatch:
                return target_word
    return None


def extract_word(data):
    """
    Extract word
    """
    out = ''
    idx = random.randint(0, len(data) - 1)
    for i in xrange(len(data)):
        if i != idx:
            out += data[i]
    return (out, data[idx])


if __name__ == '__main__':
    sys.exit(0 if main() else 1)
