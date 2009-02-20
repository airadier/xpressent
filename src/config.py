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

from ConfigParser import SafeConfigParser
from user import home
import os
import sys
import inspect

CONFIG_FILE = 'xpressent.conf'

SECTION_DISPLAY = 'display'
OPTION_PDFLIB = 'pdflib'
OPTION_FULLSCREEN = 'fullscreen'
OPTION_KEEP_ASPECT = 'keep_aspect'
OPTION_QUALITY = 'quality'

SECTION_SLIDESHOW = 'slideshow'
OPTION_PRELOAD = 'preload'
OPTION_CACHE_SIZE = 'cache_size'

SECTION_XPDF = 'xpdf'
OPTION_XPDFPATH = 'xpdfpath'

conf_file = SafeConfigParser()
module_path = os.path.dirname(inspect.getabsfile(sys.modules[__name__]))

for config_path in (
    os.path.join(home, '.' + CONFIG_FILE),
    os.path.join(home, '.xpressent', CONFIG_FILE),
    os.path.join('/etc', CONFIG_FILE),
    os.path.join(module_path, CONFIG_FILE)):

    print config_path
    if os.path.exists(config_path): 
        print "Reading: ",config_path
        conf_file.read(config_path)
        break

def get(section, option, default=None):
    if not conf_file.has_section(section):
        conf_file.add_section(section)
    if not conf_file.has_option(section, option):
        conf_file.set(section, option, str(default))
    return conf_file.get(section, option)

def getbool(section, option, default=None):
    return get(section, option, default).lower() in ('true', '1', 'enable' , 'yes')

###############################
### Section Display
###############################

if not conf_file.has_section(SECTION_DISPLAY):
    conf_file.add_section(SECTION_DISPLAY)

if not conf_file.has_option(SECTION_DISPLAY, OPTION_PDFLIB):
    conf_file.set(SECTION_DISPLAY, OPTION_PDFLIB, 'poppler')
pdflib = conf_file.get(SECTION_DISPLAY, OPTION_PDFLIB)

if not conf_file.has_option(SECTION_DISPLAY, OPTION_FULLSCREEN):
    conf_file.set(SECTION_DISPLAY, OPTION_FULLSCREEN, repr(False))
fullscreen = conf_file.getboolean(SECTION_DISPLAY, OPTION_FULLSCREEN)

if not conf_file.has_option(SECTION_DISPLAY, OPTION_KEEP_ASPECT):
    conf_file.set(SECTION_DISPLAY, OPTION_KEEP_ASPECT, repr(True))
keep_aspect = conf_file.getboolean(SECTION_DISPLAY, OPTION_KEEP_ASPECT)

if not conf_file.has_option(SECTION_DISPLAY, OPTION_QUALITY):
    conf_file.set(SECTION_DISPLAY, OPTION_QUALITY, repr(1.0))
quality = conf_file.getfloat(SECTION_DISPLAY, OPTION_QUALITY)

###############################
### Section SlideShow
###############################

if not conf_file.has_section(SECTION_SLIDESHOW):
    conf_file.add_section(SECTION_SLIDESHOW)

if not conf_file.has_option(SECTION_SLIDESHOW, OPTION_PRELOAD):
    conf_file.set(SECTION_SLIDESHOW, OPTION_PRELOAD, repr(1))
preload = conf_file.getint(SECTION_SLIDESHOW, OPTION_PRELOAD)

if not conf_file.has_option(SECTION_SLIDESHOW, OPTION_CACHE_SIZE):
    conf_file.set(SECTION_SLIDESHOW, OPTION_CACHE_SIZE, repr(5))
cache_size = conf_file.getint(SECTION_SLIDESHOW, OPTION_CACHE_SIZE)

###############################
### Section XPDF
###############################

if not conf_file.has_section(SECTION_XPDF):
    conf_file.add_section(SECTION_XPDF)

if not conf_file.has_option(SECTION_XPDF, OPTION_XPDFPATH):
    conf_file.set(SECTION_XPDF, OPTION_XPDFPATH, '')
xpdfpath = conf_file.get(SECTION_XPDF, OPTION_XPDFPATH)

###############################
### Others
###############################

window_size = (400,240)
