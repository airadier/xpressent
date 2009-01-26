from ConfigParser import SafeConfigParser


CONFIG_FILE = 'xpressent.conf'

SECTION_DISPLAY = 'display'

OPTION_FULLSCREEN = 'fullscreen'
OPTION_KEEP_ASPECT = 'keep_aspect'
OPTION_QUALITY = 'quality'

SECTION_SLIDESHOW = 'slideshow'

OPTION_PRELOAD = 'preload'
OPTION_CACHE_SIZE = 'cache_size'


conf_file = SafeConfigParser()
conf_file.read(CONFIG_FILE)

if not conf_file.has_section(SECTION_DISPLAY):
    conf_file.add_section(SECTION_DISPLAY)

if not conf_file.has_option(SECTION_DISPLAY, OPTION_FULLSCREEN):
    conf_file.set(SECTION_DISPLAY, OPTION_FULLSCREEN, repr(False))
fullscreen = conf_file.getboolean(SECTION_DISPLAY, OPTION_FULLSCREEN)

if not conf_file.has_option(SECTION_DISPLAY, OPTION_KEEP_ASPECT):
    conf_file.set(SECTION_DISPLAY, OPTION_KEEP_ASPECT, repr(True))
keep_aspect = conf_file.getboolean(SECTION_DISPLAY, OPTION_KEEP_ASPECT)

if not conf_file.has_option(SECTION_DISPLAY, OPTION_QUALITY):
    conf_file.set(SECTION_DISPLAY, OPTION_QUALITY, repr(1.0))
quality = conf_file.getfloat(SECTION_DISPLAY, OPTION_QUALITY)

if not conf_file.has_section(SECTION_SLIDESHOW):
    conf_file.add_section(SECTION_SLIDESHOW)

if not conf_file.has_option(SECTION_SLIDESHOW, OPTION_PRELOAD):
    conf_file.set(SECTION_SLIDESHOW, OPTION_PRELOAD, repr(1))
preload = conf_file.getint(SECTION_SLIDESHOW, OPTION_PRELOAD)

if not conf_file.has_option(SECTION_SLIDESHOW, OPTION_CACHE_SIZE):
    conf_file.set(SECTION_SLIDESHOW, OPTION_CACHE_SIZE, repr(5))
cache_size = conf_file.getint(SECTION_SLIDESHOW, OPTION_CACHE_SIZE)

window_size = (400,240)
