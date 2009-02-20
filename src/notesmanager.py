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

import os

class NotesManager():
    
    def __init__(self, file):
        self.notes = []

        f = open(file, "r")
        signature = f.read(4).lower()
        if signature != '%xpr':
            print "%s is not a XPR file" % file
            self.pdf_file = file
            f.close()
            return

        self.pdf_file = os.path.splitext(file)[0] + ".pdf"
        
        current_note = u""
        
        lines = f.readlines()[1:]
        for line in lines:
            if line.startswith("-----"):
                self.notes.append(current_note)
                current_note = u""
            else:
                current_note = current_note + line.decode('utf-8')
        self.notes.append(current_note)
        f.close()
            
    def get_pdf_file(self):
        return self.pdf_file
    
    def get_notes(self, page):
        if page < len(self.notes):
            return self.notes[page]
        else:
            return ""
                          
