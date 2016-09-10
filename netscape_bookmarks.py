#!/usr/bin/env python
# -*- coding: utf-8; indent-tabs-mode: nil; python-indent: 2 -*-

"""From:
    https://github.com/tibonihoo/wateronmars/blob/master/wom_river/utils/netscape_bookmarks.py
"""

"""Read bookmarks saved in a "Netscape bookmark" format
as exported by Microsoft Internet Explorer or Delicious.com (and
initially of course by Netscape).

Assumptions:
- The file is a Netscape bookmark file.
  See a doc at http://msdn.microsoft.com/en-us/library/aa753582%28v=VS.85%29.aspx
- There is only one record by line.
- If a decription/comment/note is attached to the bookmark, it is on
  a line prefixed with <DD> (and nothing else but the note should be
  on the same line).

License: 2-clause BSD

Copyright (c) 2013, Thibauld Nion
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

1. Redistributions of source code must retain the above copyright
notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright
notice, this list of conditions and the following disclaimer in the
documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED ²AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import sys
import re

def parse_netscape_bookmarks(bookmarkHTMFile):
    """Extract bookmarks and return them in a list of dictionaries formatted in the following way: [ {"url":"http://...", "title":"the title", "private":"0"/"1", "tags":"tag1,tag2,...", "posix_timestamp"="<unix time>", "note":"description"}]
        Raise a ValueError if the format is wrong.
    """
    BOOKMARK_LINE_PREFIX = "<DT>"
    BOOKMARK_NOTE_PREFIX = "<DD>"

    # Regular expression to extract info about the bookmark
    RE_BOOKMARK_URL = re.compile('HREF="(?P<url>[^"]+)"')
    RE_BOOKMARK_COMPONENTS = {
        "posix_timestamp" : re.compile('ADD_DATE="(?P<posix_timestamp>\d+)"'),
        #"tags"   : re.compile('TAGS="(?P<tags>[\w,]+)"'),
        #"tags"   : re.compile('TAGS="(?P<tags>[\w,\s?]+)"'),
        "tags"   : re.compile('TAGS="(?P<tags>.*?)"'),
        "private": re.compile('PRIVATE="(?P<private>\d)"'),
        "title"  : re.compile('<A[^>]*>(?P<title>[^<]*)<'),
    }

    bookmark_list = []
    last_line_is_bmk = False
    correct_doctype_found = False
    for line in bookmarkHTMFile.splitlines():
        line = line.lstrip()
        if line.startswith("<!DOCTYPE NETSCAPE-Bookmark-file-1>"):
          correct_doctype_found = True
          continue
        if line.rstrip() and not correct_doctype_found:
          raise ValueError("Couldn't find a correct DOCTYPE in the bookmark file (wrong format?)")
        if not line.rstrip():
          continue
        if line.startswith(BOOKMARK_LINE_PREFIX):
          # we will successively apply the various regexes until we get
          # all the bookmark's info
          m = RE_BOOKMARK_URL.search(line)
          if not m:
            # No url => skip this line
            continue
          bmk = {"url":m.group("url")}
          bmk['line'] = line
          for cpnt_name,cpnt_re in RE_BOOKMARK_COMPONENTS.items():
            m = cpnt_re.search(line)
            if m: bmk[cpnt_name] = m.group(cpnt_name)
          bookmark_list.append(bmk)
          last_line_is_bmk = True
        elif last_line_is_bmk and line.startswith(BOOKMARK_NOTE_PREFIX):
          last_line_is_bmk = False
          bookmark_list[-1]["note"] = line[4:].strip()
          bookmark_list[-1]['line'] += line[4:].strip()
        else:
          last_line_is_bmk = False
    return bookmark_list

if __name__ == '__main__':

    bookmarks = parse_netscape_bookmarks(open(sys.argv[1], 'r+').read())
    print "Found %d bookmarks" % len(bookmarks)
    print bookmarks[0]
