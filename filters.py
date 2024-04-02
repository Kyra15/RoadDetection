# import necessary libraries
import cv2
import numpy as np
import math


# warps an image given a set a vertices
def warping(img, mask_vert, screen_vert):
    matrixy = cv2.getPerspectiveTransform(mask_vert, screen_vert)
    result = cv2.warpPerspective(img, matrixy, (img.shape[1], img.shape[0]))
    return result


# un-warps an image given a set of vertices
def unwarped(img, mask_vert, screen_vert):
    matrix2 = cv2.getPerspectiveTransform(screen_vert, mask_vert)
    result = cv2.warpPerspective(img, matrix2, (img.shape[1], img.shape[0]))
    return result


# detects the HoughLines within a frame
def detect_hough(image):
    lines = cv2.HoughLines(image, 1, np.pi / 180, 100)
    line_coords = []

    if lines is not None:
        for r_theta in lines:
            # perform calculations onto the returned polar coordinates to convert them into cartesian ones

            arr = np.array(r_theta[0], dtype=np.float64)
            r, theta = arr
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a * r
            y0 = b * r
            x1 = int(x0 + 1000 * (-b))
            y1 = int(y0 + 1000 * (a))
            x2 = int(x0 - 1000 * (-b))
            y2 = int(y0 - 1000 * (a))

            # get the slope of each of the HoughLines returned and append those if they are not horizontal
            try:
                slope = round((y2 - y1) / (x2 - x1))
            except:
                slope = 999

            if not (-1 < slope < 1):
                line_coords.append([(x1, y1), (x2, y2)])

        # return the final list of HoughLines
        return line_coords


# check and filter the given HoughLines
def check_hough(good_lines, og, extra_pix=0):
    good_dist = []
    good = []
    mid_line = []

    # if the given lines is not empty,
    # check to make sure each of the lines are at least 20 pixels away from each other
    # append all the good lines to a seperate list
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

        # to prevent a divide by zero error, check to make sure that at least 2 lines were detected
        # calculate the average of two of the endpoints of the outputted lines
        # draw the final midline and return the original image and midline coordinates
        if good_dist is not None:
            for i in range(len(good_dist)):
                good.append(
                    (good_dist[i][0][0], good_dist[i][0][1], good_dist[i][1][0], good_dist[i][1][1]))
            if len(good) >= 2:
                mid_line = [(round((good[0][0] + good[1][0]) / 2), round((good[0][1] + good[1][1]) / 2)),
                            (round((good[0][2] + good[1][2]) / 2), round((good[0][3] + good[1][3]) / 2))]
                cv2.line(og, mid_line[0], mid_line[1], (0, 0, 255), 50, cv2.LINE_AA)

    else:
        return og, mid_line
    return og, mid_line


# average 2 lines given their start and end coordinates
def average_lines(line1_start, line1_end, line2_start, line2_end):
    # calculate midpoints of each line
    line1_midpoint = ((line1_start[0] + line1_end[0]) / 2, (line1_start[1] + line1_end[1]) / 2)
    line2_midpoint = ((line2_start[0] + line2_end[0]) / 2, (line2_start[1] + line2_end[1]) / 2)

    # get the average of the midpoints
    avg_midpoint = ((line1_midpoint[0] + line2_midpoint[0]) / 2, (line1_midpoint[1] + line2_midpoint[1]) / 2)

    # calculate the slope of each line
    # if there is a zero division error, set the slope to some arbitrarily high number
    try:
        slope1 = abs((line1_end[1] - line1_start[1]) / (line1_end[0] - line1_start[0]))
    except ZeroDivisionError:
        slope1 = 999

    try:
        slope2 = abs((line2_end[1] - line2_start[1]) / (line2_end[0] - line2_start[0]))
    except ZeroDivisionError:
        slope2 = 999

    # average the slopes and intercepts
    avg_slope = (slope1 + slope2) / 2
    avg_intercept = avg_midpoint[1] - avg_slope * avg_midpoint[0]

    # get the endpoints of the averaged line
    x1_avg = min(line1_start[0], line1_end[0], line2_start[0], line2_end[0])
    x2_avg = max(line1_start[0], line1_end[0], line2_start[0], line2_end[0])
    y1_avg = avg_slope * x1_avg + avg_intercept
    y2_avg = avg_slope * x2_avg + avg_intercept

    # return the coordinates for the average line
    return (round(x1_avg), round(y1_avg)), (round(x2_avg), round(y2_avg))


# using template matching, look for a left turn arrow that matches a previously stored arrow
# if that is found, display the word "left"
def detect_arrow_left(frame):
    frame_bw = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    template = cv2.imread('left_turn_temp.png', 0)
    res = cv2.matchTemplate(frame_bw, template, cv2.TM_CCOEFF_NORMED)
    threshold = 0.8
    loc = np.where(res >= threshold)
    for pt in zip(*loc[::-1]):
        cv2.putText(frame, "left", (50, 100), fontFace=1, fontScale=8.0, color=(0, 0, 0), thickness=8)
    return frame


# using template matching, look for a right turn arrow that matches a previously stored arrow
# if that is found, display the word "right"
def detect_arrow_right(frame):
    frame_bw = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    template = cv2.imread('right_turn_temp.png', 0)
    res = cv2.matchTemplate(frame_bw, template, cv2.TM_CCOEFF_NORMED)
    threshold = 0.8
    loc = np.where(res >= threshold)
    for pt in zip(*loc[::-1]):
        cv2.putText(frame, "right", (50, 100), fontFace=1, fontScale=8.0, color=(0, 0, 0), thickness=8)
    return frame



