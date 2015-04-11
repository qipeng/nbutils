import glob
import sys
import shutil
import os.path as op

CODESTART = "### YOUR CODE HERE"
CODEEND = "### END YOUR CODE"

if len(sys.argv) != 3:
	print "Usage: python %s old-directory new-directory" % (sys.argv[0])
	sys.exit(0)

def parseNotebook(name):
	blocks = []
	current = []
	studentblock = False
	with open(name, "r") as fin:
		for line in fin:
			line = line.strip()
			if line[1:].strip().startswith(CODESTART):
				blocks += [(studentblock, current)]
				current = [line]
				studentblock = True
			elif line[1:].strip().startswith(CODEEND):
				current += [line]
				blocks += [(studentblock, current)]
				current = []
				studentblock = False
			else:
				current += [line]

		blocks += [(studentblock, current)]

	return blocks

def stitchNotebook(old, new):
	newblocks = parseNotebook(new)
	oldblocks = parseNotebook(old)
	if len(newblocks) != len(oldblocks) or len(newblocks) <= 0 or len(oldblocks) <= 0:
		print "Error trying to merge IPython notebooks: notebook structure has been modified. Please proceed manually to merge starter code from '%s' into '%s'." % (new, old)
		return

	# make backup
	dirname = op.dirname(old)
	fileparts = op.splitext(op.basename(old))
	shutil.copy(old, dirname + "/" + fileparts[0] + "_backup" + fileparts[1])

	with open(old, 'w') as f:
		for i in xrange(len(newblocks)):
			studentblock, block = newblocks[i]
			if studentblock:
				for l in oldblocks[i][1]:
					f.write("%s\n" % l)
			else:
				for l in block:
					f.write("%s\n" % l)

def replaceFile(old, new):
	shutil.copy(new, old)

def updateDir(old, new):
	if op.exists(new) and (not op.exists(old)):
		shutil.copytree(new, old)

	for newname in glob.glob(new + "/*"):
		basename = op.basename(newname)
		ext = op.splitext(basename)[-1]
		oldname = old + "/" + basename
		if op.isdir(newname):
			updateDir(oldname, newname)
		else:
			if ext == ".ipynb":
				stitchNotebook(oldname, newname)
			else:
				replaceFile(oldname, newname)

updateDir(sys.argv[1], sys.argv[2])