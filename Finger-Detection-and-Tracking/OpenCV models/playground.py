#-*- coding: utf-8 -*-
import cv2
import numpy as np
'''
원본 이미지 or 헤세츄 이미지 칼러 뽑기
'''

def main():
    image = cv2.imread("/home/kicker/Finger-Detection-and-Tracking/Sample images/house.tiff", 1)

    blue, green, red = cv2.split(image)
    rows, columns, channels = image.shape

    output = np.empty((rows, columns * 3, 3), np.uint8)

    output[:, 0:columns] = cv2.merge([blue, blue, blue])
    output[:, columns:columns * 2] = cv2.merge([green, green, green])
    output[:, columns * 2:columns * 3] = cv2.merge([red, red, red])

    hsvimage = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    hue, satr, vlue = cv2.split(hsvimage)
    hsvoutput = np.concatenate((hue, satr, vlue), axis=1)

    cv2.imshow("Sample Image", image)   #원본 이미지 컬러
    cv2.imshow("Output Image", output)
    cv2.imshow("HSV Image", hsvoutput)  #헤세츄 이미지 컬러

    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
