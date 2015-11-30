import os
import time
import random
import argparse
import requests

from lxml import etree

import src.utils


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('out_dir')
    parser.add_argument('--id')
    parser.add_argument('--bound')
    parser.add_argument('--rand_bound')
    args = parser.parse_args()

    items_ids = []

    if args.id:
        items_ids.append(int(args.id))
    elif args.bound:
        start, end = args.bound.split(':')
        for i in xrange(int(start), int(end) + 1):
            items_ids.append(i)
    elif args.rand_bound:
        start, end, count = args.rand_bound.split(':')
        random.seed(time.time())
        items_ids = set()
        while 1:
            if len(items_ids) == int(count):
                break
            k = random.randrange(int(start), int(end) + 1)
            if k in items_ids:
                continue
            items_ids.add(k)
        items_ids = sorted(items_ids)

    pbar = src.utils.ProgressBar('$', len(items_ids))

    j = 0
    for i in items_ids:
        j += 1
        pbar.update(j)

        fp = os.path.join(args.out_dir, str(i))
        if os.path.exists(fp):
            continue

        ret = requests.get('http://vk.com/foaf.php?id={}'.format(i))
        if ret.status_code != 200:
            print 'ERROR', ret.status_code, ret.reason
            continue

        #try:
        #    doc = etree.fromstring(ret.content)
        #except etree.LxmlError as ex:
        #    print 'ERROR', i, str(ex)

        with open(fp, 'wb') as f:
            f.write(ret.content)

    pbar.finish()
