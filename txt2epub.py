#!/usr/bin/env python3
# coding:utf-8

# Creater: Andy Lau
# Modify by zhu1979
# Convert Chinese novel text file into an epub file.
# Assume each chapter has been converted to html,

import sys
import os
import time
import mimetypes
import shutil
import re
import zipfile
import codecs

from lxml import etree
from docopt import docopt


inputcode = ''

usage_info = """
Usage: txt2epub.py  --output <outputfolder>  --name <name>  --author <author>| --help
Arguments:
    --output    folder where EPUB will be created or updated
    --name      name of content that will be displayed in epub
    --author    author of the book
    --help      display this message """


def make_new_epub_folder(options):
    ''' given docopt's arguments dict:
    create an empty epub folder if it does not exist '''
    epubdir = os.path.abspath(os.path.join(
        os.curdir, options['<outputfolder>']))

    if not os.path.isdir(epubdir):
        os.makedirs(epubdir)

    # name = options['<name>'].replace(' ', '-')
    EPUBdir = os.path.join(epubdir, 'OEBPS')
    METAdir = os.path.join(epubdir, 'META-INF')

    Textdir = os.path.join(EPUBdir, 'Text')
    Stylesdir = os.path.join(EPUBdir, 'Styles')

    if not os.path.isdir(EPUBdir):
        os.mkdir(EPUBdir)
    if not os.path.isdir(METAdir):
        os.mkdir(METAdir)
    if not os.path.isdir(Textdir):
        os.mkdir(Textdir)
    if not os.path.isdir(Stylesdir):
        os.mkdir(Stylesdir)
    return True


def zh2unicode(stri):
    """Auto converter encodings to unicode
    It will test utf8,gbk,big5,jp,kr to converter"""
    for c in ('utf-8', 'gbk', 'big5', 'jp', 'euc_kr', 'utf16', 'utf32'):
        try:
            return stri.decode(c)
        except:
            pass
    return stri


def zh2utf8(stri):
    """Auto converter encodings to utf8
    It will test utf8,gbk,big5,jp,kr to converter"""
    for c in ('utf-8', 'gbk', 'big5', 'jp', 'euc_kr', 'utf16', 'utf32'):
        try:
            return stri.decode(c).encode('utf8')
        except:
            pass
    return stri


def is_chapter_title(line):
    # if re.match(ur"[正文]*\s*[第终][0123456789一二三四五六七八九十百千万零 　\s]*[章部集节卷]", unicode(line,'utf-8')) :
    reg1 = re.compile(r'\s*[第终][0123456789一二三四五六七八九十百千万零 　\s]*[章部集节卷]')
    reg2 = re.compile(r'^[0-9]{1,4} .*')
    reg3 = re.compile(r'^\s*[第终卷][0123456789一二三四五六七八九十零〇百千两]*[章回部节集卷].*')
    reg4 = re.compile(r'^[ 　\t]*((\s*#+ )|(第\s*[0-9零一二三四五六七八九十百]{1,6}\s*[卷章节回])).*')
    if reg1.match(zh2utf8(line)):
        return True
    elif reg2.match(zh2utf8(line)):
        return True
    elif reg3.match(zh2utf8(line)):
        return True
    elif reg4.match(zh2utf8(line)):
        return True
    else:
        return False


def write_style_css(filepath):
    filepath = os.path.join(filepath, r'OEBPS\Styles')
    css = '''/*定义字体名称*/
    @font-face {
        font-family: "h1";
        src: local("FZSongKeBenXiuKaiS-R-GB");
    }

    @font-face {
        font-family: "h2";
        src: local("FZQingKeBenYueSongS-R-GB");
    }

    @font-face {
        font-family: "h3";
        src: local("FZQingKeBenYueSongS-R-GB");
    }

    @font-face {
        font-family: "zw";
        src: local("FZBoYaFangKanSongK");
    }

    @font-face {
        font-family: "st";
        src: local("FZNewShuSong-Z10S");
    }

    body {
        padding: 0%;
        margin-top: 0px;
        margin-bottom: 0px;
        margin-left: 0px;
        margin-right: 0px;
        line-height: 110%;
        orphans: 0;
        widows: 0;
    }

    p {
        font-family: "zw";
        font-size: 125%;
        line-height: 110%;
        text-indent: 0em;
        margin-top: 4px;
        margin-bottom: 0px;
        margin-left: 0px;
        margin-right: 0px;
        orphans: 0;
        widows: 0;
    }

    div {
        line-height: 110%;
    }

    .booktitle {
        font-size: 200%;
        font-family: "h1";
        text-align: right;
        margin-top: 200px;
        margin-right: 40px;
    }

    .bookauthor {
        font-size: 100%;
        font-family: "h3";
        text-align: right;
        margin-right: 40px;
    }

    h2,
    .titlel2std {
        color: pink;
        margin-top: 0;
        line-height: 100%;
        text-align: right;
        border-style: none solid none none;
        /*上，右，下，左*/
        border-width: 0px 20px 0px 0px;
        border-right-color: mediumvioletred;
        background-color: palevioletred;
        padding: 20px 5px 5px 5px;
        page-break-before: always;
        font-weight: bold;
        font-size: x-large;
        font-family: "h2", "zw", serif;
    }'''
    with open(os.path.join(filepath, 'stylesheet.css'), 'w', encoding='utf-8') as f:
        f.write(css)
        f.close()


def makechapterhtml(filepath, chapter, chapnum):
    filepath = os.path.join(filepath, r'OEBPS\Text')
    with open(os.path.join(filepath, '{:0>4d}.xhtml'.format(chapnum)), 'w', encoding='utf-8') as f:
        f.write(r'<?xml version="1.0" encoding="UTF-8"?>')
        f.write("""
        <html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
        <head>
                <title>"""+bookname+"""</title>
                <link rel="stylesheet" href="../Styles/stylesheet.css" type="text/css" />
        </head>
        <body>""")
        f.write('        <h2>' + chapter[0] + '</h2>\n')
        f.write(chapter[1] + '\n')
        f.write("""
        </body>
        </html>""")
        f.close()


def writeopffile(filepath, manifest, spine):
    index_tpl = '''<?xml version="1.0" encoding="utf-8" standalone="no"?>
<package version="3.0" xmlns="http://www.idpf.org/2007/opf" unique-identifier="uid">
    <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
        <dc:identifier id="uid">txt2epub.1.1</dc:identifier>
        <dc:title>%(bname)s</dc:title>
        <dc:creator>%(artname)s</dc:creator>
        <dc:language>zh-CN</dc:language>
        <meta property="dcterms:modified">%(moditime)s</meta>
    </metadata>
    <manifest>
        %(manifest)s
    </manifest>
    <spine toc="ncx">
        %(spine)s
    </spine>
    <guide>
        <reference href="OEBPS/0000.xhtml" type="text" title="Beginning"/>
    </guide>
</package>'''

    currenttime = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.localtime())

    with open(os.path.join(filepath, r'OEBPS\content.opf'), 'w', encoding='utf-8') as f:
        f.write(index_tpl % {
            'bname': bookname,
            'artname': author,
            'moditime': currenttime,
            'manifest': manifest,
            'spine': spine,
        })


def writencxfile(filepath, navpoint):
    index_ncx = '''<?xml version="1.0" encoding="UTF-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
<head>
    <meta name="dtb:uid" content="txt2epub.1.1"/>
    <meta name="dtb:depth" content="1"/>
    <meta name="dtb:totalPageCount" content="0"/>
    <meta name="dtb:maxPageNumber" content="0"/>
</head>
<docTitle>
    <text>%(bname)s</text>
</docTitle>
<docAuthor>
    <text>%(artname)s</text>
</docAuthor>
<navMap>
    %(navpoint)s
</navMap>
</ncx>'''

    with open(os.path.join(filepath, r'OEBPS\toc.ncx'), 'w', encoding='utf-8') as f:
        f.write(index_ncx % {
            'bname': bookname,
            'artname': author,
            'navpoint': navpoint,
        })


def writenavfile(filepath, olli):
    index_nav = '''<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
<head>
    <title>Table of Contents</title>
</head>
<body epub:type="frontmatter">
    <nav epub:type="toc" id="toc"><h1>Table of Contents</h1>
    <ol>
        %(olli)s
    </ol>
    </nav>
</body>
</html>'''

    with open(os.path.join(filepath, r'OEBPS\Text\nav.xhtml'), 'w', encoding='utf-8') as f:
        f.write(index_nav % {'olli': olli})


def make_container(docoptions):
    epubfolder = docoptions['<outputfolder>']
    metafolder = os.path.join(epubfolder, 'META-INF')

    if not os.path.exists(metafolder):
        os.makedirs(metafolder)
    containerpath = os.path.join(metafolder, "container.xml")
    container = '''<?xml version="1.0"?>
<container xmlns="urn:oasis:names:tc:opendocument:xmlns:container" version="1.0">
    <rootfiles>
        <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
    </rootfiles>
</container>'''
    with open(containerpath, 'w', encoding='utf-8') as f:
        f.write(container)
        f.close()


if __name__ == "__main__":
    arguments = docopt(usage_info, sys.argv[1:])
    outputfolder = arguments['<outputfolder>']
    bookname = arguments['<name>']
    author = arguments['<author>']
    make_new_epub_folder(arguments)

    chapters = []
    chaptercontent = ''
    chaptername = ''
    pre_chap_title = ''
    frontpage = 0

    bookfile = open('{bname}.txt'.format(bname=bookname), 'r')
    for linenum, line in enumerate(bookfile.readlines()):
        line = line.strip()
        if len(line):
            line = zh2utf8(line)
            if is_chapter_title(line):
                pre_chap_title = chaptername
                chaptername = line
                if linenum != 0 and not frontpage:
                    frontpage = 1
                    pre_chap_title = '前  言'

                if frontpage:
                    chapters.append((pre_chap_title, chaptercontent))
                else:
                    chapters.append((chaptername, chaptercontent))
                chaptercontent = ''
            else:
                chaptercontent += '        <p>'+'　　'+line+'</p>\n'
    chapters.append((chaptername, chaptercontent))
    bookfile.close()

    # EPUB2, abandon in EPUB3
    manifest = '<item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>\n'
    manifest += '        <item id="toc" properties="nav" href="Text/nav.xhtml" media-type="application/xhtml+xml"/>\n'
    manifest += '        <item id="css" href="Styles/stylesheet.css" media-type="text/css"/>\n'
    spine = ''
    olli = ''

    # EPUB2, abandon in EPUB3
    navpoint = ''
    # chapter_file_list = []

    for chapternum, chapter in enumerate(chapters):
        makechapterhtml(outputfolder, chapter, chapternum)
        manifest += '        <item id="chapter_{:0>4d}" href="Text/{:0>4d}.xhtml" media-type="application/xhtml+xml"/>\n'.format(
            chapternum, chapternum)
        spine += '        <itemref idref="chapter_{:0>4d}" />\n'.format(
            chapternum)

        olli += '''<li id="chapter_{:0>4d}">
          <a href="../Text/{:0>4d}.xhtml">{chaptitle}</a>
        </li>
          '''.format(chapternum, chapternum, chaptitle=chapter[0])

    # EPUB2, abandon in EPUB3
        navpoint += '''    <navPoint class="chapter" id="chapter_{seq}" playOrder="{chapnum}">
        <navLabel>
        <text>{chaptitle}</text>
        </navLabel>
        <content src="Text/{seq}.xhtml"/>
    </navPoint> '''.format(seq='{:0>4d}'.format(chapternum), chaptitle=chapter[0], chapnum=chapternum)
        chapter_file_name = '{:0>4d}.xhtml'.format(chapternum)
        # chapter_file_list.append(chapter_file_name)

    # write OEBPS/stylesheet.css
    write_style_css(outputfolder)

    # write package.opf
    writeopffile(outputfolder, manifest, spine)

    # EPUB2, abandon in EPUB3
    # write toc.ncx
    writencxfile(outputfolder, navpoint)

    # write nav.xhtml
    writenavfile(outputfolder, olli)

    # write container.xml
    epubfolder = arguments['<outputfolder>']

    make_container(arguments)

    # write mimetype
    with open(os.path.join(epubfolder, 'mimetype'), 'w', encoding='utf-8') as f:
        f.write('application/epub+zip')
        f.close()

    # finally zip everything into the destination
    out = zipfile.ZipFile(os.path.join(epubfolder, '{bname}.epub'.format(
        bname=bookname)), "w", zipfile.ZIP_DEFLATED)

    out.write(epubfolder + "/mimetype", "mimetype", zipfile.ZIP_STORED)
    out.write(epubfolder + "/META-INF/container.xml",
              "META-INF/container.xml", zipfile.ZIP_DEFLATED)

    for root, dirs, files in os.walk(epubfolder):
        for name in files:
            if name != 'mimetype' and name != 'container.xml':
                fname = os.path.join(root, name)
                new_path = os.path.normpath(fname.replace(epubfolder, ''))
                out.write(fname, new_path)

    out.close()
