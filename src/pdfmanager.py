# Copyright 2009, Alvaro J. Iradier
# This file is part of xPressent.
#
# xPressent is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# xPressent is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with xPressent.  If not, see <http://www.gnu.org/licenses/>.

import config
import cStringIO
import pygame

import sys
import os
import inspect
from subprocess import Popen, PIPE

class PDFManagerBase(object):
    def __init__(self, pdf_file, quality):
        self.file = pdf_file
        self.set_quality(quality)

    def get_render_size(self, screen_size, page_size):
        render_w = int(screen_size[0] * self.quality)
        render_h = int(screen_size[1] * self.quality)

        if config.keep_aspect:
            #Calculate and compare
            page_ratio = float(page_size[0]) / float(page_size[1])
            screen_ratio = float(screen_size[0]) / float(screen_size[1])
            if page_ratio >= screen_ratio:
                dest_w = render_w
                dest_h = render_w / page_ratio
            else:
                dest_h = render_h
                dest_w = render_h * page_ratio
        else:
            dest_w, dest_h = render_w, render_h

        return int(dest_w), int(dest_h)

    def get_num_pages(self):
        return 0

    def set_quality(self, quality):
        self.quality = quality

    def render_page(self, page_num, size):
        return None


class PopplerPDFManager(PDFManagerBase):

    def __init__(self, pdf_file, quality):
        PDFManagerBase.__init__(self, pdf_file, quality)
        self.doc = poppler.document_new_from_file('file://%s' % pdf_file, None)

    def get_num_pages(self):
        return self.doc.get_n_pages()


    def render_page(self, page_num, size):

        page = self.doc.get_page(page_num)
        page_w, page_h = page.get_size()

        dest_w, dest_h = self.get_render_size(size, (page_w, page_h))

        img = cairo.ImageSurface(cairo.FORMAT_RGB24, dest_w, dest_h)
        context = cairo.Context(img)
        context.scale(dest_w/page_w, dest_h/page_h)
        context.set_source_rgb(1.0, 1.0, 1.0)
        context.rectangle(0, 0, page_w, page_h)
        context.fill()
        page.render(context)
        f = cStringIO.StringIO()
        img.write_to_png(f)
        f.seek(0)
        return pygame.image.load(f, 'img.png');


class XPDFManager(PDFManagerBase):

    def __init__(self, pdf_file, quality):
        PDFManagerBase.__init__(self, pdf_file, quality)

        f = open(pdf_file, "r")
        signature = f.read(4).lower()
        f.close()
        if signature != '%pdf':
            raise Exception("%s is not a PDF file" % pdf_file)

        if not config.xpdfpath:
            self.xpdfpath = ''
        elif os.path.isabs(config.xpdfpath):
            self.xpdfpath = config.xpdfpath
        else:
            self.xpdfpath = os.path.join(
                os.path.dirname(inspect.getabsfile(sys.modules[__name__])),
                config.xpdfpath)

        self.pdfinfoexe = os.path.join(self.xpdfpath, 'pdfinfo')
        self.pdftoppmexe = os.path.join(self.xpdfpath, 'pdftoppm')

        pipe = Popen((self.pdfinfoexe, pdf_file),
            stdout=PIPE, stderr=PIPE, universal_newlines = True)
        pipe.wait()
        info_lines = pipe.stdout.read().splitlines()
        errors = pipe.stderr.read()

        if errors:
            raise Exception, errors

        self.pdf_info = {}
        for line in info_lines:
            key = line[:line.find(':')]
            self.pdf_info[key] = line[line.find(':') + 1:].lstrip()


        page_size = self.pdf_info['Page size'].split()
        self.page_size = (int(page_size[0]), int(page_size[2]))

    def get_num_pages(self):
        return int(self.pdf_info['Pages'])

    def render_page(self, page_num, size):

        dest_w, dest_h = self.get_render_size(size, self.page_size)

        res = int((dest_w * 72) / self.page_size[0])
        cmdargs = (self.pdftoppmexe,
            '-r', str(res), '-f', str(page_num + 1), '-l',str(page_num + 1),
            self.file, 'tmpslide')
        pipe = Popen(cmdargs, stdout=PIPE, stderr=PIPE, universal_newlines = True)
        pipe.wait()

        if os.path.exists('tmpslide-%06d.ppm' % (page_num + 1)):
            tmpfile = 'tmpslide-%06d.ppm' % (page_num + 1)
        else:
            tmpfile = 'tmpslide-%02d.ppm' % (page_num + 1)
        img = pygame.image.load(tmpfile)
        os.unlink(tmpfile)
        return img


PDFManager = None
if config.pdflib == 'poppler':
    try:
        import poppler
        import cairo
        PDFManager = PopplerPDFManager
        print "Using Poppler for PDF rendering"
    except ImportError:
        print "Poppler or Cairo libraries missing, using alternate renderer"

if not PDFManager:
    PDFManager = XPDFManager
    print "Using XPDF for PDF rendering"
