#!/usr/bin/env python

from gimpfu import *

def gaussSeidelPoissonSolver(srcImg, dstImg, mask, height, width):

    import copy
    #srcImg = copy.deepcopy(image)
    #dstImg = copy.deepcopy(image)
    N = [[(i != 0) + (j != 0) + (i != width - 1) + (j != height - 1) \
            for j in xrange(height)] for i in xrange(width)]
    b = [[0 for j in xrange(height)] for i in xrange(width)]
    for x in xrange(width):
        for y in xrange(height):
            if x != 0:
                if mask[x - 1][y] != 0:
                    b[x][y] += (srcImg[x][y] - srcImg[x - 1][y])
                if mask[x - 1][y] == 0:
                    b[x][y] += srcImg[x - 1][y]
            if x != width - 1:
                if mask[x + 1][y] != 0:
                    b[x][y] += (srcImg[x][y] - srcImg[x + 1][y])
                if mask[x + 1][y] == 0:
                    b[x][y] += srcImg[x + 1][y]
            if y != 0:
                if mask[x][y - 1] != 0:
                    b[x][y] += (srcImg[x][y] - srcImg[x][y - 1])
                if mask[x][y - 1] == 0:
                    b[x][y] += srcImg[x][y - 1]
            if y != height - 1:
                if mask[x][y + 1] != 0:
                    b[x][y] += (srcImg[x][y] - srcImg[x][y + 1])
                if mask[x][y + 1] == 0:
                    b[x][y] += srcImg[x][y + 1]
    #B = math.sqrt(sum([b[i][j] * b[i][j] for i in xrange(width) \
    #                for j in xrange(height) if mask[i][j] == 1]))
    #gimp.message(str(N[0][0]) + ' ' + str(N[1][1]))
    #gimp.message(str(b[100][100]) + ' ' + str(dstImg[100][100]) + ' ' + str(N[100][100]) + ' ' + str(b[102][100]) + ' ' + str(dstImg[102][100]) + ' ' + str(N[102][100]) + " " + \
    #str((b[100][100] + dstImg[101][100] + dstImg[99][100] + dstImg[100][101] + dstImg[100][99]) / N[100][100]))
    #error = B
    count = 0

    while(count < 300):
        count += 1
        error = 0
        for x in xrange(width):
            #gimp.message(str(x))
            for y in xrange(height):
                if(mask[x][y] == 0):
                    continue
                nextValue = b[x][y]
                if x != 0:
                    if mask[x - 1][y] != 0:
                        nextValue += dstImg[x - 1][y]
                if x != width - 1:
                    if mask[x + 1][y] != 0:
                        nextValue += dstImg[x + 1][y]
                if y != 0:
                    if mask[x][y - 1] != 0:
                        nextValue += dstImg[x][y - 1]
                if y != height - 1:
                    if mask[x][y + 1] != 0:
                        nextValue += dstImg[x][y + 1]
                nextValue = 1.0 * nextValue / N[x][y]
                '''
                if nextValue < 0:
                    nextValue = 0
                if nextValue > 255:
                    nextValue = 255
                '''
                #error += (dstImg[x][y] - nextValue) ** 2
                dstImg[x][y] = int(round(nextValue))
                #dstImg[x][y] = 0
        for x in xrange(width):
            #gimp.message(str(x))
            for y in xrange(height):
                if(dstImg[x][y] > 255):
                    dstImg[x][y] = 255
                if(dstImg[x][y] < 0):
                    dstImg[x][y] = 0
    return dstImg


def getOneColorPixel(layer, color):
    width = layer.width
    height = layer.height
    pixels = [[layer.get_pixel(x, y)[color] for y in xrange(height)] for x in xrange(width)]
    return pixels

def setOneColorPixel(layer, color, pixels, mask):
    width = layer.width
    height = layer.height
    for x in xrange(width):
        for y in xrange(height):
            #if(mask[x][y] == 0):
            #    continue
            pixel = layer.get_pixel(x, y)
            newpixel = pixel[:color] + tuple([pixels[x][y]]) + pixel[color + 1:]
            layer.set_pixel(x, y, newpixel)

def doSeamlessen(img, layer, mask):
    width = layer.width
    height = layer.height
    #selection = pdb.gimp_image_get_selection(img)
    #mask = getOneColorPixel(selection, 0)
    gimp.message('start')
    layer0 = img.layers[0]
    layer1 = img.layers[1]

    newpixels0 = getOneColorPixel(layer0, 0)
    newpixels1 = getOneColorPixel(layer1, 0)
    newpixels = gaussSeidelPoissonSolver(newpixels0, newpixels1, mask, height, width)
    #newpixels = newpixels1
    setOneColorPixel(layer1, 0, newpixels, mask)

    gimp.message(str(mask[0][0]))
    newpixels0 = getOneColorPixel(img.layers[0], 1)
    newpixels1 = getOneColorPixel(img.layers[1], 1)
    newpixels = gaussSeidelPoissonSolver(newpixels0, newpixels1, mask, height, width)
    setOneColorPixel(layer1, 1, newpixels, mask)

    newpixels0 = getOneColorPixel(layer0, 2)
    newpixels1 = getOneColorPixel(layer1, 2)
    newpixels = gaussSeidelPoissonSolver(newpixels0, newpixels1, mask, height, width)
    setOneColorPixel(layer1, 2, newpixels, mask)

    '''
    newpixels = getOneColorPixel(layer, 1)
    newpixels = gaussSeidelPoissonSolver(newpixels, mask, height, width)
    setOneColorPixel(layer, 1, newpixels)

    newpixels = getOneColorPixel(layer, 2)
    newpixels = gaussSeidelPoissonSolver(newpixels, mask, height, width)
    setOneColorPixel(layer, 2, newpixels)
    '''

def seamlessen(img, layer) :
    ''' seamlessen selected region
    '''
    # Indicates that the process has started.
    gimp.progress_init("seamlessening " + layer.name + "...")

    # Set up an undo group, so the operation will be undone in one step.
    pdb.gimp_image_undo_group_start(img)

    # Iterate over all the pixels and convert them to gray.

    try:
        selection = pdb.gimp_image_get_selection(img)
        mask = getOneColorPixel(selection, 0)
        doSeamlessen(img, layer, mask)
        img.layers[1].update(0, 0, layer.width, layer.height)

    except Exception as err:
        gimp.message("Unexpected error: " + str(err))
        print err

    # Close the undo group.
    pdb.gimp_image_undo_group_end(img)

    # End progress.
    pdb.gimp_progress_end()

register(
    "python_fu_seamlessen",
    "seamless",
    "seamlessing selected region",
    "Liujunyi",
    "Open source",
    "2015",
    "<Image>/Filters/Test/seamlessen",
    "*",
    [],
    [],
    seamlessen)

main()
