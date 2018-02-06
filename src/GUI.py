# -*- coding: utf-8 -*-
from __future__ import print_function
from teachablerobots.src.GridSpace import *

# import the necessary packages
from PIL import Image
from PIL import ImageTk
import tkinter as tk
from tkinter import *

import random

class Application(Frame):
    """A GUI application which which generates random number and gets user input"""

    def __init__(self, master): #initialize newly created Application object
        """Initialize the frame"""
        Frame.__init__(self, master) # super(Application, self).__init__(master) in python 3
        self.grid()
        self.create_widgets()
        self.number = random.randint(1, 101)

    def create_widgets(self):
        """Get user inputs"""
        # create instruction label
        Label(self, text = "I'm thinking of a number between 1 and 100.").grid(row = 0, column = 0, sticky = W)
        Label(self, text = "Try and guess it in as few attempts as possible!").grid(row = 1, column = 0, sticky = W)

        # create guess input prompt label and entry
        Label(self, text = "Take a guess:").grid(row = 2, column = 0, sticky = W)
        self.guess_ent = Entry(self)
        self.guess_ent.grid(row = 2, column = 1, sticky = W)

        # create start game prompt label and submit button
        Label(self, text = "Press submit to start the game!").grid(row = 3, column = 0, sticky = W)
        Button(self, text = "Submit", command = self.run_game).grid(row = 3, column = 1, sticky = W)


        # create submit button
        #Button(self, text = "Submit", command = )

        # create computer feedback text box
        self.text = Text(self, width = 75, height = 10, wrap = WORD)
        self.text.grid(row = 4, column = 0, columnspan = 4)

    def run_game(self):
        """Generate number and get user input"""
        guess = int(self.guess_ent.get())

        if guess != self.number:
            print_text = "You guessed {0}.".format(guess)

            if guess > self.number:
                print_text += " That's too high. Guess lower..."
            elif guess < self.number:
                print_text += " That's too low. Guess higher..."

            self.text.delete(0.0, END)
            self.text.insert(0.0, print_text)

            self.guess_ent.delete(0, END)
        else:
            print_text = "That's the right number! Well done!"
            self.text.delete(0.0, END)
            self.text.insert(0.0, print_text)

#   main
root = Tk()
root.title("Guess my number game!")
app = Application(root)
root.mainloop()







##import time
##t1 = time.time()
##
##G = GridSpace()
##while(True):
##    G.Update(lambda: G.ShowFrame(True))
##    t2 = time.time()
##    if(t2-t1 > 5):
##        break
##






