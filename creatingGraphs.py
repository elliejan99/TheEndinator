import matplotlib.pyplot as plt
import numpy as np

def makeGraph(a1, a2, y):
    box = np.ones(1) / 1
    returns_smooth = np.convolve(a2[1:], box, mode='same')
    plt.clf()
    plt.plot(a1[1:], returns_smooth)
    plt.title('The Endinator')
    plt.ylabel(y)
    plt.xlabel('Distance')
    plt.savefig('distance' + y + '.png')

if __name__ == '__main__':
    yaw = open("distanceYaw.txt")
    arrows = open("distanceArrows.txt")

    arrowArray = []
    distanceArrow = []
    distanceYaw = []
    yawArray = []

    for line in arrows:
        temp = line.split("\t")
        arrowArray.append(float(temp[2]))
        distanceArrow.append(float(temp[1]))

    for line in yaw:
        temp = line.split("\t")
        yawArray.append(float(temp[3]))
        
        if temp[2] == "60.0":
            temp[2] = 11
        distanceYaw.append(float(temp[2]))

    makeGraph(distanceArrow, arrowArray, "arrow")
    makeGraph(distanceYaw, yawArray, "yaw")

    yaw.close()
    arrows.close()