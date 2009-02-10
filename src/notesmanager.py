import os

class NotesManager():
    
    def __init__(self, file):
        f = open(file, "r")
        signature = f.read(4).lower()
        self.notes = []
        if signature != '%xpr':
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
        f.close()
            
    def get_pdf_file(self):
        return self.pdf_file
    
    def get_notes(self, page):
        if page < len(self.notes):
            return self.notes[page]
        else:
            return ""
                          
