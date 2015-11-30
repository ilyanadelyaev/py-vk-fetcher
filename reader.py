import os
import argparse
import datetime

import sqlite3

import src.parser
import src.db
import src.utils




if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('in_dir')
    parser.add_argument('db_name')
    parser.add_argument('--id')
    args = parser.parse_args()

    con = sqlite3.connect(args.db_name)

    with con:
        cur = con.cursor()

        src.db.create_tables(cur)

        if args.id:
            ids = [args.id]
        else:
            ids = [fn for fn in os.listdir(args.in_dir)]

        pbar = src.utils.ProgressBar('$', len(ids))

        j = 0
        for fn in ids:
            j += 1
            pbar.update(j)

            with open(os.path.join(args.in_dir, fn), 'rb') as f:
                data = f.read()
                if not data:
                    continue

            obj = src.parser.parse_html(fn, data)

            if not obj:
                continue

            try:
                src.db.add_record(cur, obj)
            except Exception as ex:
                print 'ERROR', fn, str(ex)
                continue

            #if args.id:
            #    import pprint
            #    pprint.pprint(obj)

        pbar.finish()
