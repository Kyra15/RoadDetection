# import necessary libraries
import cv2
import numpy as np
import math
import time


# applies a grayscale filter, gaussian blur, and canny image filter on a frame given and returns the final frame
def filters(img):
    gray_image = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    blur = cv2.GaussianBlur(gray_image, (5, 5), 0)
    cannyimg = cv2.Canny(blur, 150, 200, apertureSize=5, L2gradient=False)
    return cannyimg


def warping(img, mask_vert, screen_vert):
    matrixy = cv2.getPerspectiveTransform(mask_vert, screen_vert)
    result = cv2.warpPerspective(img, matrixy, (img.shape[1], img.shape[0]))
    # cv2.imshow("warp", result)
    return result


def unwarped(img, mask_vert, screen_vert):
    matrix2 = cv2.getPerspectiveTransform(screen_vert, mask_vert)
    result = cv2.warpPerspective(img, matrix2, (img.shape[1], img.shape[0]))
    # cv2.imshow("unwarp", result)
    return result


def detect_hough(image):
    lines = cv2.HoughLines(image, 1, np.pi / 180, 100)

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


def check_hough(good_lines, img, og, extra_pix=0):
    good_dist = []
    good = []
    mid_line = []

    if good_lines is not None:
        for i in good_lines:
            x1, y1 = i[0]
            x2, y2 = i[1]

            dist = any(math.dist([x1, y1], [pt1[0], pt1[1]]) < 20 or
                       math.dist([x2, y2], [pt2[0], pt2[1]]) < 20
                       for pt1, pt2 in good_dist
                       )

            if not dist:
                good_dist.append([[x1 + extra_pix, y1], [x2 + extra_pix, y2]])

        # to prevent a divide by zero error, check to make sure that at least 1 line was detected
        # calculate the average of two of the endpoints of the outputted lines
        if good_dist is not None:
            # print("dist", len(good_dist))
            for i in range(len(good_dist)):
                # cv2.line(og, (good_dist[i][0][0], good_dist[i][0][1]),
                # (good_dist[i][1][0], good_dist[i][1][1]), (0, 0, 255), 20, cv2.LINE_AA)
                good.append(
                    (good_dist[i][0][0], good_dist[i][0][1], good_dist[i][1][0], good_dist[i][1][1]))
            if len(good) >= 2:
                mid_line = [(round((good[0][0] + good[1][0]) / 2), round((good[0][1] + good[1][1]) / 2)),
                            (round((good[0][2] + good[1][2]) / 2), round((good[0][3] + good[1][3]) / 2))]
                cv2.line(og, mid_line[0], mid_line[1], (0, 0, 255), 50, cv2.LINE_AA)

    else:
        return og, mid_line
    return og, mid_line


def average_lines(line1_start, line1_end, line2_start, line2_end):
    # Calculate midpoints of each line
    line1_midpoint = ((line1_start[0] + line1_end[0]) / 2, (line1_start[1] + line1_end[1]) / 2)
    line2_midpoint = ((line2_start[0] + line2_end[0]) / 2, (line2_start[1] + line2_end[1]) / 2)

    # Average the midpoints
    avg_midpoint = ((line1_midpoint[0] + line2_midpoint[0]) / 2, (line1_midpoint[1] + line2_midpoint[1]) / 2)

    try:
        # Calculate slope of each line
        slope1 = (line1_end[1] - line1_start[1]) / (line1_end[0] - line1_start[0])
    except ZeroDivisionError:
        slope1 = 999

    try:
        slope2 = (line2_end[1] - line2_start[1]) / (line2_end[0] - line2_start[0])
    except ZeroDivisionError:
        slope2 = 999

    # Average the slopes
    avg_slope = (slope1 + slope2) / 2

    # Calculate intercept of the averaged line
    avg_intercept = avg_midpoint[1] - avg_slope * avg_midpoint[0]

    # Calculate endpoints of the averaged line
    x1_avg = min(line1_start[0], line1_end[0], line2_start[0], line2_end[0])
    x2_avg = max(line1_start[0], line1_end[0], line2_start[0], line2_end[0])
    y1_avg = avg_slope * x1_avg + avg_intercept
    y2_avg = avg_slope * x2_avg + avg_intercept

    return [round(x1_avg), round(y1_avg)], [round(x2_avg), round(y2_avg)]


