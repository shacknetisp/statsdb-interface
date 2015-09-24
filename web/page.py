# -*- coding: utf-8 -*-
import math
import cgi


def calc(sel, maxnum, listcount):
    if 'page' in sel.qopt:
        try:
            page = int(sel.qopt["page"][0])
            page = max(page, 1)
            page = min(page, math.ceil(maxnum / listcount))
        except ValueError:
            page = 1
    else:
        page = 1
    page -= 1
    page *= listcount
    return page


def getlist(currentpage, listcount):
    return list(range(currentpage, currentpage + listcount))


def make(path, current, maxnum, count):
    around = 3
    current = int(current / count) + 1
    plink = lambda n, t: '<a href="%s?page=%d">%s</a>' % (path,
        n, cgi.escape(str(t))) if n != 1 else '<a href="%s">%s</a>' % (
            path, cgi.escape(str(t)))
    maxpages = math.ceil(maxnum / count)
    ret = '<ul class="pagelist">'
    if current > 1:
        ret += '<li>%s</li>' % plink(current - 1, "<")
    nlinks = list(range(current - around, current + around + 1))
    if 1 not in nlinks:
        ret += '<li>%s</li>%s' % (plink(1, 1),
            '...' if current - around >= 1 + 2 else '')
    for link in nlinks:
        if link >= 1 and link <= maxpages:
            if link == current:
                ret += '<li>%d</li>' % link
            else:
                ret += '<li>%s</li>' % plink(link, link)
    if maxpages not in nlinks:
        ret += '%s<li>%s</li>' % (
            '...' if current + around <= maxpages - 2 else '',
            plink(maxpages, maxpages))
    if current < maxpages:
        ret += '<li>%s</li>' % plink(current + 1, ">")
    ret += "</ul>"
    return ret