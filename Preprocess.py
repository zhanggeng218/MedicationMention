import pprint
import os

def readFile(fname):
    with open(fname, 'r') as f:
        lines = f.readlines()
    return lines

def stripEndOfLines(lines):
    newlines = []
    for line in lines:
        newlines.append(line.strip('\n') + " ")
    return newlines

def processFiles(pth, out_prefix):
    for fname in os.listdir(pth):
        in_name = pth + "/" + fname
        out_name = pth + "/" + out_prefix + fname

        lines = readFile(in_name)
        newlines = stripEndOfLines(lines)
        newcontent = "".join(newlines)

        o = open(out_name, 'w')
        o.write(newcontent)
        o.close()


folder_path = os.getcwd() + "/tmp"
out_prefix = "n_"
processFiles(folder_path, out_prefix)
