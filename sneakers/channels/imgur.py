# Imports
from PIL import Image
import math

class MessageToImageMaker(object):

    def __init__(self,pixelSize,bitsPerPixel):
        self.pixelSize = max(pixelSize,3)
        self.bitsPerPixel = min(bitsPerPixel,4)
        # More parameters. These should not change!
        self.colorDivisions = 2**self.bitsPerPixel
        self.maxPixelBits = 8
        self.maxPixelValue = 2**self.maxPixelBits
        # These are the possible values (0-255) of the R,G,B values of each pixel
        self.pixelValues = [int((i+0.5)*self.maxPixelValue/self.colorDivisions) for i in range(self.colorDivisions)]

    def createImage(self,message,fileName,fileFormat):

        # Convert message into byte array
        bytes = bytearray(message,'UTF-8')

        # If there is no message, then exit.
        if len(bytes) == 0:
            print "The message has no size"
            exit(0)

        # Currently, we have an array of bytes, each 8 bits long. However, we want to be able to convert this to an array of
        # bits of bitsPerPixel bits long.
        # Initialize output array and populate buffer
        imageBits = []
        buffer = bytes[0]
        bufferBits = 8
        bytesIndex = 1
        # Keep going till there are more bytes to analyze in the bytes array
        while bytesIndex < len(bytes) or bufferBits != 0:
            # If the buffer is less than 8 bits, then add more information to it
            if bufferBits < 8 and bytesIndex < len(bytes):
                buffer<<=8
                buffer+=bytes[bytesIndex]
                bytesIndex+=1
                bufferBits+=8
            # Note that, unless we have run out of bytes to read, the buffer must be at least 8 bits long.
            # If the number of bits in the buffer is greater than the number of bits per unit of information needed:
            if bufferBits >= self.bitsPerPixel:
                imageBits.append((buffer>>(bufferBits-self.bitsPerPixel)))
                buffer%=2**(bufferBits-self.bitsPerPixel)
                bufferBits-=self.bitsPerPixel
            # Otherwise:
            else:
                imageBits.append(buffer<<(self.bitsPerPixel-bufferBits))
                bufferBits = 0

        # Because we can fit RGB values per cell, the number of pixels we need is a third of the size of imageBits
        imageSize = (int)(math.ceil(math.sqrt(len(imageBits)/3)))
        # We are going to create a black image, and then start filling in pixel values
        image = Image.new('RGB',((imageSize+1)*self.pixelSize,(imageSize+1)*self.pixelSize),"black")
        pixels = image.load()
        done = False
        for row in range(imageSize):
            if done:
                break
            for column in range(imageSize):
                messageIndex = 3*(row*imageSize + column)
                # We could probably save some time by breaking when we know we have no more bits to read
                if messageIndex >= len(imageBits):
                    done = True
                    break
                r = self.pixelValues[imageBits[messageIndex]] if messageIndex < len(imageBits) else 0
                messageIndex+=1
                g = self.pixelValues[imageBits[messageIndex]] if messageIndex < len(imageBits) else 0
                messageIndex+=1
                b = self.pixelValues[imageBits[messageIndex]] if messageIndex < len(imageBits) else 0
                # Each "pixel" isn't literally 1 pixel. It is a square of actual pixels that are all the same
                # so that compression does not get rid of any information easily
                for inner_row2 in range(self.pixelSize):
                    for inner_column2 in range(self.pixelSize):
                        pixels[column*self.pixelSize+inner_column2,row*self.pixelSize+inner_row2] = (r,g,b)
        # Make calibration pixels on the right and bottom sides of the picture
        for calibIndex in range(imageSize):
            for inner_row2 in range(self.pixelSize):
                    for inner_column2 in range(self.pixelSize):
                        pixels[imageSize*self.pixelSize+inner_column2,calibIndex*self.pixelSize+inner_row2]= (0,0,0) if calibIndex%2==1 else (255,255,255)
                        pixels[calibIndex*self.pixelSize+inner_column2,imageSize*self.pixelSize+inner_row2]= (0,0,0) if calibIndex%2==1 else (255,255,255)
        # Calibration pixel for the bottom right corner
        for inner_row2 in range(self.pixelSize):
            for inner_column2 in range(self.pixelSize):
                pixels[imageSize*self.pixelSize+inner_column2,imageSize*self.pixelSize+inner_row2]= (0,0,0) if imageSize%2==1 else (255,255,255)

        # Save the new image File
        image.save(fileName,fileFormat)


    def readImage(self,fileName):

        image = Image.open(fileName)
        pixels = image.load()

        rowDivisions = []
        columnDivisions = []
        width,height = image.size[0],image.size[1]

        blackCalib = 15
        whiteCalib = 240

        counter = 0
        white = True
        for row in range(height):
            pixelValue = pixels[width-1,row]
            avgValue = float(sum(pixelValue))/len(pixelValue)
            if (white and avgValue > whiteCalib) or (not white and avgValue < blackCalib):
                counter+=1
            else:
                columnDivisions.append(counter)
                counter=1
                white = not white

        counter = 0
        white = True
        for column in range(width):
            pixelValue = pixels[column,height-1]
            avgValue = float(sum(pixelValue))/len(pixelValue)
            if (white and avgValue > whiteCalib) or (not white and avgValue < blackCalib):
                counter+=1
            else:
                rowDivisions.append(counter)
                counter=1
                white = not white

        offset = self.pixelValues[0]
        divisions = self.pixelValues[1]-offset
        imageBits = []
        minRowPixel = 0
        for row in range(len(rowDivisions)):
            maxRowPixel = minRowPixel + rowDivisions[row] - 1
            minColumnPixel = 0
            for column in range(len(columnDivisions)):
                maxColumnValue = minColumnPixel + columnDivisions[column] - 1
                totalR = 0
                totalG = 0
                totalB = 0
                for innerRow in range(minRowPixel+1,maxRowPixel):
                    for innerColumn in range(minColumnPixel+1,maxColumnValue):
                        totalR+=pixels[innerColumn,innerRow][0]
                        totalG+=pixels[innerColumn,innerRow][1]
                        totalB+=pixels[innerColumn,innerRow][2]
                imageBits.append(max(int(round((float(totalR )/((rowDivisions[row]-2)*(columnDivisions[column]-2))-offset)/divisions)),0))
                imageBits.append(max(int(round((float(totalG)/((rowDivisions[row]-2)*(columnDivisions[column]-2))-offset)/divisions)),0))
                imageBits.append(max(int(round((float(totalB)/((rowDivisions[row]-2)*(columnDivisions[column]-2))-offset)/divisions)),0))
                minColumnPixel = maxColumnValue + 1
            minRowPixel = maxRowPixel + 1

        bytes = []
        buffer = imageBits[0]
        bufferBits = self.bitsPerPixel
        bytesIndex = 1
        # Keep going till there are more bytes to analyze in the bytes array
        while bytesIndex < len(imageBits) or bufferBits != 0:
            # If the buffer is less than 8 bits, then add more information to it
            if bufferBits < 8 and bytesIndex < len(imageBits):
                buffer<<=self.bitsPerPixel
                buffer+=imageBits[bytesIndex]
                bytesIndex+=1
                bufferBits+=self.bitsPerPixel
            # Note that, unless we have run out of bytes to read, the buffer must be at least 8 bits long.
            # If the number of bits in the buffer is greater than the number of bits per unit of information needed:
            else:
                if bufferBits >= 8:
                    bytes.append((buffer>>(bufferBits-8)))
                    buffer%=2**(bufferBits-8)
                    bufferBits-=8
                # Otherwise:
                else:
                    bytes.append(buffer<<(8-bufferBits))
                    bufferBits = 0
        for i in reversed(range(len(bytes))):
            if bytes[i]==0:
                bytes.pop()
            else:
                break

        return ''.join(chr(i) for i in bytes)




message = "Hello, is this the Krusty Krab? No, this is Patrick."
mtim = MessageToImageMaker(10,4)
mtim.createImage(message,"image.jpg","JPEG")
print mtim.readImage("image.jpg")
