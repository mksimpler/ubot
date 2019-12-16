import numpy
import cv2
from imutils import contours, grab_contours


def detect_numbers(image, number_fonts, max_digits):
    """
    Method to ocr numbers (using OpenCV).
    Returns int.
    """
    text = []

    crop = cv2.resize(image, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
    thresh = cv2.threshold(crop, 0, 255, cv2.THRESH_OTSU)[1]

    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    cnts = grab_contours(cnts)
    cnts = contours.sort_contours(cnts, method="left-to-right")[0]

    if len(cnts) > max_digits:
        return 0

    for c in cnts:
        scores = []

        (x, y, w, h) = cv2.boundingRect(c)
        roi = thresh[y:y + h, x:x + w]
        row, col = roi.shape[:2]

        width = round(abs((50 - col)) / 2) + 5
        height = round(abs((94 - row)) / 2) + 5
        resized = cv2.copyMakeBorder(roi, top=height, bottom=height, left=width, right=width, borderType=cv2.BORDER_CONSTANT, value=[0, 0, 0])

        for font in number_fonts:
            result = cv2.matchTemplate(resized, font, cv2.TM_CCOEFF_NORMED)
            (_, score, _, _) = cv2.minMaxLoc(result)
            scores.append(score)

        text.append(str(numpy.argmax(scores)))

    text = "".join(text)
    return int(text)
