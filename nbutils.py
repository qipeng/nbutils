import json
import os.path as op
import numpy as np
from ast import literal_eval
import re

STUDENT_CODE_BEGIN = "### YOUR CODE HERE"
STUDENT_CODE_END = "### END YOUR CODE"
AUTOGRADER_OUTPUT_BEGIN = "=== For autograder ==="

class Notebook:
    def __init__(self, filename = None):
        if filename:
            self.parse(filename)

    def parse(self, filename = None):
        if not filename:
            raise(Exception("Notebook parsing error: empty file name"))
            return False

        if not op.exists(filename):
            raise(Exception("Notebook parsing error: file '%s' doesn't exist" % filename))
            return False

        with open(filename, 'r') as f:
            self.rawjson = json.load(f)

        self.markdownCells = []
        # put a dummy 0-th code cell and its outputs to make code blocks 1-indexed
        self.codeCells = [[]]
        self.cellOutputs = [[]]

        codecellIdx = 0
        markdownBuffer = []
        for cell in self.rawjson["cells"]:
            celltype = cell["cell_type"]
            if celltype == "code":
                self.markdownCells += [markdownBuffer]
                self.codeCells += [cell["source"]]
                self.cellOutputs += [cell["outputs"]]
                markdownBuffer = []
                codecellIdx += 1
            elif celltype == "markdown":
                markdownBuffer += [cell["source"]]

        self.markdownCells += [markdownBuffer]

        return True

class Autograder:
    def __init__(self, filename = None):
        self.parse(filename)

    def parse(self, filename = None):
        self.notebook = Notebook(filename)

        self.studentBlocks = []
        self.studentOutputs = []

        for cId in xrange(len(self.notebook.codeCells)):
            blocksBuffer = []
            inStudentCode = False
            for line in self.notebook.codeCells[cId]:
                stripped = line.strip()
                if stripped.startswith(STUDENT_CODE_BEGIN):
                    if not inStudentCode:
                        studentBlock = [line]
                        inStudentCode = True
                    else:
                        raise(Exception("Malformed notebook file"))
                elif stripped.startswith(STUDENT_CODE_END):
                    if inStudentCode:
                        studentBlock += [line]
                        blocksBuffer += [studentBlock]
                        inStudentCode = False
                    else:
                        raise(Exception("Malformed notebook file"))
                elif inStudentCode:
                    studentBlock += [line]
            self.studentBlocks += [blocksBuffer]

            inAutograderOutput = False
            outputsbuffer = []
            for output in self.notebook.cellOutputs[cId]:
                outputsbuffer = []
                if "name" in output and output["name"] == "stdout":
                    linebuffer = []
                    for line in output["text"]:
                        stripped = line.strip()
                        if stripped.startswith(AUTOGRADER_OUTPUT_BEGIN):
                            inAutograderOutput = True
                            continue
                        if inAutograderOutput:
                            linebuffer += [stripped]
                            bufferstr = " ".join(linebuffer)

                            # try parsing the current buffer
                            try:
                                bufferstr = bufferstr.replace("array", "")

                                if bufferstr.startswith("("):
                                    parsed = literal_eval(bufferstr)
                                elif bufferstr.startswith("["):
                                    if "," not in bufferstr:
                                        # NumPy ndarrays aren't the best things to print directly...
                                        bufferstr = re.sub(r"\](\s+)\[", "],[", bufferstr)
                                        bufferstr = re.sub(r"(\s+)\]", r"]", bufferstr)
                                        bufferstr = re.sub(r"(\d)\s", r"\1,", bufferstr)
                                        parsed = np.array(literal_eval(bufferstr))
                                    else:
                                        parsed = literal_eval(bufferstr)
                                else:
                                    parsed = bufferstr

                                linebuffer = []
                                outputsbuffer += [("stdout", parsed)]
                            except Exception as e:
                                pass

            self.studentOutputs += [outputsbuffer]

if __name__ == "__main__":
    ag = Autograder('wordvec_sentiment.ipynb')

    print ag.studentBlocks[4]