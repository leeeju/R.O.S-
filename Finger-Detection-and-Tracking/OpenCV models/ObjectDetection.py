#-*- coding: utf-8 -*-
import cv2
import numpy as np
'''
마스크 연산과 B.G.R 칼러 추출하기
'''

def main():
    # Blue Color Object Range
    blue_low = np.array([110, 100, 100])
    blue_high = np.array([130, 255, 255])

    # Green Color Object Range
    green_low = np.array([50, 100, 100])
    green_high = np.array([70, 255, 255])

    # Red Color Object Range
    red_low = np.array([0, 100, 100])
    red_high = np.array([10, 255, 255])

    windowOrignal = "Orignal Live Feed"  # 원본영상
    windowMasked = "Masked Window Feed"  # 마스크 영상
    windowColorObject = "Color Object Tracked"  #B.G.R 추출연산

    capture = cv2.VideoCapture(0)

    if capture.isOpened():
        flag, frame_bgr = capture.read()
    else:
        flag = False

    while flag:

        flag, frame_bgr = capture.read()

        frame_hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)

        masker_red = cv2.inRange(frame_hsv, red_low, red_high)  # inRange 범위 안에 들어가면
        masked_green = cv2.inRange(frame_hsv, green_low, green_high)

        red_green_masked = cv2.bitwise_or(masker_red, masked_green)

        target = cv2.bitwise_and(frame_bgr, frame_bgr, mask=red_green_masked)

        cv2.imshow(windowColorObject, target)
        cv2.imshow(windowMasked, red_green_masked)
        cv2.imshow(windowOrignal, frame_bgr)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cv2.destroyAllWindows()
    capture.release()


if __name__ == '__main__':
    main()
