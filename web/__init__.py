# -*- coding: utf-8 -*-
import cgi
import math
import cfg


def page(content, title="", css="", debug=""):
    #Insert content into template
    #Replace non-ascii characters with XML escapes
    ret = open("files/html/base.html").read().format(
        content=content,
        title=(": " + title) if title else "", css=css, debuginfo=debug).encode(
            'ascii', 'xmlcharrefreplace')
    return ret


# HTML Table Generator
class Table:

    class TR:

        def __init__(self, table):
            self.table = table
            self.tds = []

        def __enter__(self):
            self.tds = []
            return self

        def __exit__(self, type, value, traceback):
            tds = ""
            for td in self.tds:
                tds += "<td>%s</td>" % td
            self.table.entries.append("""
            <tr>
            {tds}
            </tr>
            """.format(tds=tds))

        def __call__(self, td=""):
            self.tds.append(str(td))

    def __init__(self, headings, title="", classes=""):
        self.headings = headings
        self.entries = []
        self.tr = self.TR(self)
        self.title = title
        self.classes = classes

    def add(self, t):
        self.tds.append(t)

    def html(self, full=False):
        headings = ""
        for h in self.headings:
            headings += "<th>%s</th>" % h
        if full:
            ret = """
            <div class='{classes}'>
                <h3>{title}</h3>
                <table>
                    <tr>
                        {headings}
                    </tr>
                    {body}
                </table>
            </div>
            """.format(headings=headings, body="".join(self.entries),
                classes=self.classes, title=self.title)
        else:
            ret = """
            <table>
                <tr>
                    {headings}
                </tr>
                {body}
            </table>
            """.format(headings=headings, body="".join(self.entries))
        return ret


# Pagination Generator
class Pager:

    def __init__(self, request, perpage, data, forcelen=None):
        self.request = request
        self.perpage = perpage
        self.data = data
        if type(self.data) is not list:
            # Convert to list (reversed, etc)
            self.data = list(self.data)
        self.lendata = len(self.data) if forcelen is None else forcelen
        self.current = self.findcurrent()

    def findcurrent(self):
        if 'page' in self.request.query:
            try:
                page = int(self.request.query["page"][0])
                page = max(page, 1)
                page = min(page, math.ceil(self.lendata / self.perpage))
            except ValueError:
                page = 1
        else:
            page = 1
        page -= 1
        page *= self.perpage
        return page

    def list(self):
        return self.data[self.current:self.current + self.perpage]

    def html(self):
        plink = lambda n, t: '<a href="%s?page=%d">%s</a>' % (self.request.path,
            n, cgi.escape(str(t))) if n != 1 else '<a href="%s">%s</a>' % (
                self.request.path, cgi.escape(str(t)))
        around = cfg.get('paginator_around')
        current = int(self.current / self.perpage) + 1
        maxpages = math.ceil(self.lendata / self.perpage)
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


# <a href> Generator
def link(start, end, text, escape=False):
    if escape:
        text = cgi.escape(text)
    return '<a href="%s%s">%s</a>' % (start, end, text)


def linkif(start, end, text, escape=False):
    end = str(end)
    text = str(text)
    if escape:
        text = cgi.escape(text)
    if end:
        return '<a href="%s%s">%s</a>' % (start, end, text)
    else:
        return '%s' % (text)
