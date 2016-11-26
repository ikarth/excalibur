# -*- coding: utf-8 -*-

def makeBook(text):
    with open("output.markdown", mode = "w", encoding = "utf8") as file:
        file.write(text)