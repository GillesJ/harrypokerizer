#!/usr/bin/env python

from lxml import html
# import urllib.request as urlRequest
from string import ascii_uppercase
import distance
from collections import OrderedDict
from terminaltables import AsciiTable
import sys

def scrape_names(names_fp):
    potter_names = []
    for c in ascii_uppercase:
        url = "http://www.hp-lexicon.org/character/?letter=" + c
        # pretend to be a chrome 47 browser on a windows 10 machine
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36"}
        req = urlRequest.Request(url, headers=headers)
        # open the url
        page = urlRequest.urlopen(req)
        # get the source code
        content = page.read()

        page_html = html.fromstring(content)
        scraped_names = page_html.xpath('//span[@itemprop="headline"]//text()')
        potter_names.extend(scraped_names)

    filter_rules = [lambda s: any(x.isupper() for x in s), # must have at least one uppercase
                    lambda s: [all(x.islower() for x in word) for word in s.split()].count(True) <= 2 # can only have two
                    #  lowercase word in name. case: "the wizards who flew to the moon"
                    ]
    filtered_potter_names = []
    for name in potter_names:
        if all(rule(name) for rule in filter_rules):
            print(name)
            filtered_potter_names.append(name)

    # with open(names_fp, 'wt') as outf:
    #     for name in potter_names:
    #         outf.write("%s\n" % name)

    with open(names_fp, 'wt') as outf:
        for name in filtered_potter_names:
            outf.write("%s\n" % name)

def read_names(names_fp):
    names = []
    for line in open(names_fp, 'rt'):
        names.append(line.strip())
    return names

def get_distance(compare_names, potter_names):
    distances = {}
    for n in compare_names:
        distances[n] = {"levenshtein": {}, "hamming": {}, "jaccard": {}, "sorensen": {}}
        for pottern in potter_names:
            dl = distance.levenshtein(n.lower(), pottern.lower(), normalized=False) # set to True if you want to normalize for length
            distances[n]["levenshtein"][dl] = pottern

            dj = distance.jaccard(n.lower(), pottern.lower())
            distances[n]["jaccard"][dj] = pottern

            ds = distance.sorensen(n.lower(), pottern.lower())
            distances[n]["sorensen"][ds] = pottern

            if len(n) == len(pottern):
                dh = distance.hamming(n.lower(), pottern.lower(), normalized=False)
                distances[n]["hamming"][dh] = pottern
    return distances

def get_separate_name_distance(compare_names, potter_names):
    compare_sep_names = []
    potter_sep_names = []
    for n in compare_names:
        compare_sep_names.extend(n.split())
        compare_sep_names = list(set(compare_sep_names))
    for pottern in potter_names:
        potter_sep_names.extend(pottern.split())
        potter_sep_names = list(set(potter_sep_names))
    return get_distance(compare_sep_names, potter_sep_names)

def print_results(dict, n):
    for k, v in dict.items():
        table_data = [['levenshtein', 'hamming', 'jaccard', 'sorensen'],]
        ovl = OrderedDict(sorted(v["levenshtein"].items()))
        ovh = OrderedDict(sorted(v["hamming"].items()))
        ovj = OrderedDict(sorted(v["jaccard"].items()))
        ovs = OrderedDict(sorted(v["sorensen"].items()))
        i = 0
        while i < n:
            for (k1, v1), (k2, v2), (k3, v3), (k4, v4) in zip(ovl.items(), ovh.items(), ovj.items(), ovs.items()):
                table_data.append(["%s (%s)" % (v1,round(k1,3)), "%s (%s)" % (v2,round(k2,3)), "%s (%s)" %
                                   (v3,round(k3,3)), "%s (%s)" % (v4,round(k4,3))])
                i+=1
        table = AsciiTable(table_data, title=k.upper())
        print(table.table, "\n")

# scrape_names(names_fp)
potternames_fp = "./potterversenames.txt"
pokenames_fp = "./pokeversenames.txt"
compare_names = sys.argv[1:]
potter_names = read_names(potternames_fp)
poke_names = read_names(pokenames_fp)
potter_names.extend(poke_names) # combine list and remove duplicates by making set
potter_names = list(set(potter_names))
full_name_distances = get_distance(compare_names, potter_names)
separate_name_distances = get_separate_name_distance(compare_names, potter_names)
print_results(full_name_distances, 5)
print_results(separate_name_distances, 5)
