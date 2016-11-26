# -*- coding: utf-8 -*-

from subprocess import call

def makePDF():
    call(["pandoc",""])

def makeBook(text):
    with open("output.markdown", mode = "w", encoding = "utf8") as file:
        file.write(text)
    #makePDF()