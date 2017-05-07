from Tkinter import *

class guiclient(Tkinter.Tk):
    def __init__(self,parent):
        Tkinter.Tk.__init__(self,parent)
        self.parent = parent
        self.initialize()
    def initialize(self):
        pass
if __name__ == "__main__":
    app = guiclient(None)
    app.title("Battleships")

    
