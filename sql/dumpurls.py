# encoding: utf-8

"""
Collect all the urls of the application

Insert them in a sqlite db

authors: raphael@softosapiens.fr
created: 2023-06-13 17:48:16 CEST
"""

import sqlite3

from django.urls import resolvers

from urbanvitaliz import urls


def collect_urls(urlpatterns, prefix=""):
    entries = []
    for p in urlpatterns:
        if isinstance(p, resolvers.URLPattern):
            pattern = f"{prefix}{p.pattern.regex.pattern}".replace("^", "")
            entry = [p.name, pattern, p.lookup_str]
            entries.append(entry)
        if isinstance(p, resolvers.URLResolver):
            sub_prefix = f"{prefix}{p.pattern.regex.pattern}"
            sub_entries = collect_urls(p.url_patterns, sub_prefix)
            entries.extend(sub_entries)
    return entries


def dump_urls(urls):
    rows = collect_urls(urls.urlpatterns)
    c = sqlite3.connect("urls.sqlite3")
    c.execute("create table urls(name,pattern,view)")
    c.executemany("insert into urls(name,pattern,view) values(?,?,?)", rows)
    c.commit()
    c.close()


dump_urls(urls)

# eof
