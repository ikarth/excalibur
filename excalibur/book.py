# -*- coding: utf-8 -*-

import subprocess

def makePDF():
    #out = subprocess.run("pandoc -D latex --latex-engine=xelatex -V documentclass=memoir --normalize --toc > template.latex ")
    #print(out)
    out = subprocess.run("pandoc -s --latex-engine=xelatex --from markdown+yaml_metadata_block --to latex+yaml_metadata_block -o output.pdf -V documentclass=scrbook --template scrbook_template.latex --normalize --toc output.markdown")
    # book --template template.latex -V geometry:paperwidth:5.5in -V geometry:paperheight:8.25in
    print(out)
    
def makeBook(text):
    with open("output.markdown", mode = "w", encoding = "utf8") as file:
        file.write(text)
    makePDF()
    
 