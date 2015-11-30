import os
import argparse
import calendar

from lxml import etree
import dateutil.parser

import src.utils


ITEMS_LISTS = set(('locationOfBirth', 'phone', 'URI', 'externalProfile', 'edu', 'school', 'university', 'job', 'workPlace', 'military'))


def iterable(o, d):
    k = d.tag.split('}')[1]
    oo = o.setdefault(k, {})
    for dd in d:
        kk = dd.tag.split('}')[1]

        if kk in oo:
            if kk not in ITEMS_LISTS:
                raise Exception('ERROR {} is list'.format(kk))

        PROCESSORS[kk](oo, dd)


def text(o, d, pr=None):
    v = d.text
    if not v:
        return
    v = v.strip()
    if not v:
        return
    k = d.tag.split('}')[1]
    if pr:
        o[k] = pr(v)
    else:
        o[k] = v


def items(o, d):
    k = d.tag.split('}')[1]
    oo = o.setdefault(k, {})
    for kk, dd in d.items():
        kk = kk.split('}')[1]
        oo[kk] = dd
    if d.text and d.text.strip():
        oo['___text___'] = d.text.strip()


def items_list(o, d):
    oo = {}
    items(oo, d)
    k, v = oo.items()[0]
    o.setdefault(k, []).append(v)


def education(o, d):
    oo = {}
    items_list(oo, d)
    ooo = {}
    iterable(ooo, d)
    k, v = oo.items()[0]
    v = v[0]
    kk, vv = ooo.items()[0]
    v.update(vv)
    v.pop('about')
    o.setdefault(k, []).append(v)


def job(o, d):
    oo = {}
    items_list(oo, d)
    ooo = {}
    iterable(ooo, d)
    k, v = oo.items()[0]
    v = v[0]
    kk, vv = ooo.items()[0]
    v.update(vv)
    v.pop('about')
    o.setdefault(k, []).append(v)


def time_value(o, d):
    oo = {}
    items(oo, d)
    k, v = oo.items()[0]
    o[k] = calendar.timegm(dateutil.parser.parse(v['date']).utctimetuple())


def skip(o, d):
    pass


PROCESSORS = {
    'Person': iterable,
    #
    'URI': items_list,
    #
    'name': text,
    'firstName': text,
    'secondName': text,
    'nick': text,
    #
    'gender': text,
    'familyStatus': text,
    #
    'birthday': text,
    'dateOfBirth': text,
    'locationOfBirth': items_list,
    #
    'location': items,
    #
    'subscribersCount': (lambda o, d: text(o, d, int)),
    'friendsCount': (lambda o, d: text(o, d, int)),
    'subscribedToCount': (lambda o, d: text(o, d, int)),
    #
    'externalProfile': items_list,
    'skypeID': text,
    'phone': items_list,
    'homepage': text,
    #
    'edu': iterable,
    'school': education,
    'university': education,
    #
    'job': iterable,
    'workPlace': job,
    'military': job,
    #
    'interest': text,
    'weblog': items,
    'bio': text,
    #
    'publicAccess': text,
    'profileState': text,
    'created': items,
    'lastLoggedIn': items,
    'modified': items,
    #
    'img': skip,
}


def parse_html(i, data):
    try:
        doc = etree.fromstring(data)
    except etree.LxmlError as ex:
        print 'ERROR', i, str(ex)
        return

    if not len(doc):
        print 'ERROR', i, 'ZERO'
        return

    obj = {}
    try:
        for d in doc:
            iterable(obj, d)
    except Exception as ex:
        print 'ERROR', i, str(ex)
        return

    return obj
