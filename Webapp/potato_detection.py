from potato_detector.python.predict import *
from PIL import Image

def hb_detect_potatoes(image_file, threshold = .5, outdir = 'segmented/'):
    hsize = 144
    wsize = 144
    boxes = hb_detector(image_file)
    image = Image.open(image_file)
    for i in range(len(boxes)):
        if (boxes[i]['tagName'] == 'potato') and (boxes[i]['probability'] >= threshold):
            imgcopy = image.copy()
            width, height = image.size
            left = round(boxes[i]['boundingBox']['left']*width)
            top = round(boxes[i]['boundingBox']['top']*height)
            wb = round(boxes[i]['boundingBox']['width']*width)
            hb = round(boxes[i]['boundingBox']['height']*height)
            if left < 0:
                left = 0
            if top < 0:
                top = 0
            if left >= width:
                left = width -1
            if top >= height:
                top = height -1
            imgcopy = imgcopy.crop((left, top, left+wb, top+hb))
            imgcopy = imgcopy.resize((wsize,hsize))
            imgcopy.save(outdir+str(i)+'.jpg')
