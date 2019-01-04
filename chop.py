import os
from sys import argv

try:
    biteSize = int(argv[1])
    print("biteSize =", biteSize)
except:
    biteSize = 1020
    print("Using default biteSize value of", biteSize)

peakThreshold = 0.3
os.system('rm chops/*.csv')
fileList = os.popen('ls raw/*.csv').read().split()
fileIndex = 0

for datafile in fileList:
    filename = datafile
    times = []
    x = []
    y = []
    z = []
    mag = []
    a = 0
    b = 0
    diffs = []
    headerEnd = False  # useful for buffered data at start

    with open(datafile) as file:
        try:
            for line in file:
                if line.rstrip() == "t,x,y,z":
                    # labels
                    headerEnd = True
                    pass
                elif len(line.rstrip().split(",")) == 4 and headerEnd is True:
                    dat = line.rstrip().split(",")
                    times.append(float(dat[0]) / 1000000.)  # seconds
                    x.append(int(dat[1]))
                    y.append(int(dat[2]))
                    z.append(int(dat[3]))
                    pass
                else:
                    # for truncated lines
                    continue
        except:
            # catch any garbled data at the start
            pass

    outIndex = 0
    for i in range(int(len(times) / biteSize)):
        outIndex = i * biteSize
        outFile = 'chops/' + "%03d" % (fileIndex + i + 1) + '.csv'
        with open(outFile, 'w+') as file:
            file.write(filename + '\n\n')
            file.write('t,x,y,z\n')
            for j in range(outIndex, outIndex + biteSize):
                file.write(
                    str(int((times[j] - times[i * biteSize]) * 1000000)) + ',' +
                    str(x[j]) + ',' +
                    str(y[j]) + ',' +
                    str(z[j]) + '\n')
    fileIndex = fileIndex + i + 1
    print(filename, str(len(times)), str(i + 1), sep="\t")
