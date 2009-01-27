import poppler
import config
import cairo
import cStringIO
import pygame

class PDFManager(object):

    def __init__(self, pdf_file, quality):
        self.doc = poppler.document_new_from_file('file://%s' % pdf_file, None)
        self.set_quality(quality)

    def get_num_pages(self):
        return self.doc.get_n_pages()
        
    def set_quality(self, quality):
        self.quality = quality

    def render_page(self, page_num, size):

        page = self.doc.get_page(page_num)
        page_w, page_h = page.get_size()

        render_w = int(size[0] * self.quality)
        render_h = int(size[1] * self.quality)

        if config.keep_aspect:
            #Calculate and compare
            page_ratio = float(page_w) / float(page_h)
            screen_ratio = float(size[0]) / float(size[1])
            if page_ratio >= screen_ratio:
                dest_w = render_w
                dest_h = render_w / page_ratio
            else:
                dest_h = render_h
                dest_w = render_h * page_ratio
        else:
            dest_w, dest_h = render_w, render_h

        img = cairo.ImageSurface(cairo.FORMAT_RGB24, render_w, render_h)
        context = cairo.Context(img)
        context.translate(
            int((render_w - dest_w)/2),
            int((render_h - dest_h)/2))
        context.scale(dest_w/page_w, dest_h/page_h)
        context.set_source_rgb(1.0, 1.0, 1.0)
        context.rectangle(0, 0, page_w, page_h)
        context.fill()
        page.render(context)
        f = cStringIO.StringIO()
        img.write_to_png(f)
        f.seek(0)
        return pygame.image.load(f, 'img.png');