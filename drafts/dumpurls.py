import csv

from django.urls import resolvers


def collect_urls(urlpatterns):
    entries = []
    for p in urlpatterns:
        if isinstance(p, resolvers.URLPattern):
            entry = [p.name, p.pattern.regex.pattern, p.lookup_str]
            entries.append(entry)
        if isinstance(p, resolvers.URLResolver):
            sub_entries = collect_urls(p.url_patterns)
            entries.extend(sub_entries)
    return entries


def dump_urls(urls):
    rows = collect_urls(urls.urlpatterns)
    print(len(rows))
    with open("urls.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerows(rows)


from urbanvitaliz import urls

dump_urls(urls)

# eof
