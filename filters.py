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
    up_bound = np.array([210, 200, 180])
    lw_bound = np.array([100, 110, 100])

    mask = cv2.inRange(image, lw_bound, up_bound)
    cv2.imshow("masking", mask)
    res = cv2.bitwise_and(image, image, mask=mask)

    f = image - res
    cv2.imshow("chroma", f)

    return f


def detect_white(image):
    up_bound = np.array([255, 255, 255])
    lw_bound = np.array([175, 175, 175])

    mask = cv2.inRange(image, lw_bound, up_bound)
    cv2.imshow("masking", mask)
    res = cv2.bitwise_and(image, image, mask=mask)

    cv2.imshow("white", res)
    return res


def detect_yellow(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    up_bound = np.array([40, 255, 255])
    lw_bound = np.array([10, 95, 95])

    mask = cv2.inRange(hsv, lw_bound, up_bound)
    cv2.imshow("masking", mask)
    res = cv2.bitwise_and(hsv, hsv, mask=mask)

    cv2.imshow("yellow", res)
    return cv2.cvtColor(res, cv2.COLOR_HSV2RGB)

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


def contouring(image, final, extra_pix=0):
    # find the contours on the image
    contours, hierarchy = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # contours = imutils.grab_contours((contours, hierarchy))

    # sort the list of contours by the contour area
    new = list(contours)
    new.sort(key=cv2.contourArea)

    # if there are at least 2 contours that have been detected
    if len(new) > 2:
        # get the 2 largest contours
        c1 = new[-1]
        c2 = new[-2]
        c3 = new[-3]

        # fit polylines to each contour
        # outline1 = cv2.approxPolyDP(c1, 4, True)
        # cv2.drawContours(final, [outline1], -1, (0, 255, 255), 15)
        #
        # outline2 = cv2.approxPolyDP(c2, 4, True)
        # cv2.drawContours(final, [outline2], -1, (0, 255, 255), 15)
        #
        # outline3 = cv2.approxPolyDP(c3, 4, True)
        # cv2.drawContours(final, [outline3], -1, (255, 0, 255), 15)

        cx1 = 0
        cy1 = 0
        cx2 = 0
        cy2 = 0
        cx3 = 0
        cy3 = 0

        try:
            M1 = cv2.moments(c1)
            cx1 = int(M1['m10'] / M1['m00']) + extra_pix
            cy1 = int(M1['m01'] / M1['m00'])

            M2 = cv2.moments(c2)
            cx2 = int(M2['m10'] / M2['m00']) + extra_pix
            cy2 = int(M2['m01'] / M2['m00'])

            M3 = cv2.moments(c3)
            cx3 = int(M3['m10'] / M3['m00']) + extra_pix
            cy3 = int(M3['m01'] / M3['m00'])
        except Exception as e:
            pass

        cv2.circle(final, (cx1, cy1), 1, (0, 0, 255), 5)
        cv2.circle(final, (cx2, cy2), 1, (255, 0, 0), 5)
        cv2.circle(final, (cx3, cy3), 1, (255, 255, 0), 5)

        midx = (cx1+cx2+cx3)/3
        mid
        # get mid and then height and then drw lies
        
        
        # poly = np.array([[cx1, cy1], [cx2, cy2], [cx3, cy3]])
        # approx = cv2.approxPolyDP(poly, 4, False)
        # cv2.drawContours(final, [approx], -1, (0, 0, 255), 3)

