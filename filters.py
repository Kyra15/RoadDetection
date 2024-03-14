# import necessary libraries
import cv2
import numpy as np


# applies a grayscale filter, gaussian blur, and canny image filter on a frame given and returns the final frame
def filters(img):
    gray_image = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    blur = cv2.GaussianBlur(gray_image, (9, 9), 0)
    cannyimg = cv2.Canny(blur, 200, 300, apertureSize=5)
    cv2.imshow("can", cannyimg)
    return cannyimg


def warping(img, vertices, og):
    matrix = cv2.getPerspectiveTransform(vertices, og)
    result = cv2.warpPerspective(img, matrix, (img.shape[1], img.shape[0]))
    cv2.imshow("warp", result)
    return result


def chroma_key(image):
    up_bound = np.array([180, 170, 170])
    lw_bound = np.array([65, 80, 75])

    mask = cv2.inRange(image, lw_bound, up_bound)
    cv2.imshow("masking", mask)
    res = cv2.bitwise_and(image, image, mask=mask)

    f = image - res
    cv2.imshow("mask", f)

    return f


def detect_hough(image):
    lines = cv2.HoughLines(image, 1, np.pi / 180, 50)

    line_coords = []

    if lines is not None:
        # The below for loop runs till r and theta values
        # are in the range of the 2d array
        for r_theta in lines:
            arr = np.array(r_theta[0], dtype=np.float64)
            r, theta = arr
            # Stores the value of cos(theta) in a
            a = np.cos(theta)

            # Stores the value of sin(theta) in b
            b = np.sin(theta)

            # x0 stores the value rcos(theta)
            x0 = a * r

            # y0 stores the value rsin(theta)
            y0 = b * r

            # x1 stores the rounded off value of (rcos(theta)-1000sin(theta))
            x1 = int(x0 + 1000 * (-b))

            # y1 stores the rounded off value of (rsin(theta)+1000cos(theta))
            y1 = int(y0 + 1000 * (a))

            # x2 stores the rounded off value of (rcos(theta)+1000sin(theta))
            x2 = int(x0 - 1000 * (-b))

            # y2 stores the rounded off value of (rsin(theta)-1000cos(theta))
            y2 = int(y0 - 1000 * (a))

            try:
                slope = round((y2 - y1) / (x2 - x1))
            except:
                slope = 999

            if not (-1 < slope < 1):
                line_coords.append([(x1, y1), (x2, y2)])
        return line_coords


