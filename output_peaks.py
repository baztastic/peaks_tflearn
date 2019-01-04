import numpy as np
from math import sqrt
import peakutils
import os
import sys

try:
    outputPeaksArg = sys.argv[1]
    if outputPeaksArg == "--output":
        outputPeaks = True
        sys.stdout.write("Plotting peaks\n")
        sys.stdout.flush()
    elif outputPeaksArg == "--no-output":
        outputPeaks = False
        sys.stdout.write("Skipping peaks\n")
        sys.stdout.flush()
except:
    outputPeaks = False
    print("Skipping peaks")
    print("Usage: python3", sys.argv[0], "--output or --no-output")

# Fitting parameters
# peakThreshold = 0.22
# peakDistance = 9
# peakNum = 10

peakThreshold = 0.3
peakDistance = 9
peakNum = 40

folder = 'id'
peaksFile = 'peaks.csv'

defaultfile = "test3.csv"
if outputPeaks is True:
    # os.system('rm mats/*.dat')
    # os.system('rm mats/npy/*.npy')
    sys.stdout.write("Writing peaks")
    sys.stdout.flush()


fileList = os.popen('ls chops/*.csv').read().split()
clearResults = os.system('rm chops/results.txt')
rawFileName = ''


# def out_mat(shortname):
#     skip = 10
#     scaleFactor = 100  # scale matrix values from 0 to scaleFactor
#     n = int(sqrt(len(fx[skip:])))
#     fxMat = np.matrix([[0] * n] * n)
#     fxMapped = scaleFactor * (fx - min(fx[skip:])) / (max(fx[skip:]) - min(fx[skip:]))
#     for i in range(n):
#         for j in range(n):
#             if i % 2 == 0:
#                 fxMat[i, j] = fxMapped[j + skip + i * n]
#             else:
#                 fxMat[i, j] = fxMapped[(n - 1 - j) + skip + i * n]

#     np.savetxt('mats/' + shortname + '.dat', fxMat, fmt='%d', delimiter='\t')
#     np.save('mats/npy/' + shortname, fxMat)


# def xy_out_mat(shortname):
#     skip = 10
#     xp = fx[skip:]
#     yp = fy[skip:]
#     xp = 100 * (xp - min(xp)) / (max(xp) - min(xp))
#     yp = 100 * (yp - min(yp)) / (max(yp) - min(yp))
#     n = len(xp)
#     m = len(yp)
#     fpMat = np.matrix([[0] * n] * n)
#     for i in range(m):
#         for j in range(n):
#             fpMat[i, j] = xp[j] * yp[i]
#             if fpMat[i, j] <= 2000:
#                 fpMat[i, j] = 0

#     # fpMapped = 100 * (fp - min(fp[skip:])) / (max(fp[skip:]) - min(fp[skip:]))

#     np.savetxt('mats/' + shortname + '.dat', fpMat, fmt='%d', delimiter='\t')
#     np.save('mats/npy/' + shortname, fpMat)


for datafile in fileList:
    filename = datafile
    times = []
    x = []
    y = []
    z = []
    a = 0
    b = 0
    diffs = []
    headerEnd = False  # useful for buffered data at start

    with open(datafile) as file:
        rawFileName = file.readline().strip()
        try:
            for line in file:
                if line.rstrip() == "t,x,y,z":
                    # labels
                    headerEnd = True
                    pass
                elif len(line.rstrip().split(",")) == 4 and headerEnd is True:
                    dat = line.rstrip().split(",")
                    #     continue
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

    for time in times:
        a = time
        diffs.append(a - b)
        b = time

    samplingPeriod = np.average(diffs)  # seconds

    n = len(x)
    k = np.arange(n)
    T = samplingPeriod * n
    frq = k[:int(n / 2)] / T

    fx = abs(np.fft.rfft(x) / n)
    fy = abs(np.fft.rfft(y) / n)
    fz = abs(np.fft.rfft(z) / n)

    indexes = peakutils.indexes(
        fx / max(fx), thres=peakThreshold, min_dist=peakDistance)
    peaks = [frq[index] for index in indexes]
    peakHeights = [fx[index] for index in indexes]

    while len(peakHeights) < peakNum:
        peakHeights.append(0.0)

    # state = ''
    rawState = ''

    if 'idling' in rawFileName:
        rawState = '0'
    elif 'drilling' in rawFileName:
        rawState = '1'
    # elif 'drilloff' in rawFileName:
    #     rawState = 2
    # else:
    #     rawState = "Indeterminate"

    # if len(indexes) == 0:
    #     state = "Drill off"
    #     pass
    # elif len(indexes) > 0 and len(indexes) <= peakNum:
    #     state = "Idling  "
    #     pass
    # elif len(indexes) > peakNum:
    #     state = "Drilling"
    #     pass
    # else:
    #     state = "Indeterminate"
    #     pass

    # with open('chops/results.txt', 'a') as file:
    #     if state == rawState:
    #         judgement = '\tCorrect!'
    #     else:
    #         judgement = '\tWrong'
    #     file.write(filename + '\t-\t' + str(len(peaks)).zfill(2) +
    #                ' peaks\t-\t' + state + judgement + '\n')

    if outputPeaks is True:
        identifier = folder + filename.strip().split('/')[1].split('.')[0]
        with open(peaksFile, 'a+') as outFile:
            outFile.write(rawState + ',' + identifier + ',')
            for peak in peakHeights[:-1]:
                outFile.write(str(peak) + ',')
            outFile.write(str(peakHeights[-1]) + '\n')
        sys.stdout.write(".")
        sys.stdout.flush()
    else:
        pass

if outputPeaks is True:
    print('done!')
# correct = int(os.popen('grep -c "Correct" chops/results.txt').read().strip())
# wrong = int(os.popen('grep -c "Wrong" chops/results.txt').read().strip())
# successRate = 100 * correct / (correct + wrong)
# print('Success rate = ' + "%0.1f" % successRate + '%')
