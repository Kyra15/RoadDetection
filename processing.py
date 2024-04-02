# import the filter file functions
from filters import *

# initialize a list with a random first coordinate
coord_r = [[(0, 0)]]
coord_l = [[(0, 0)]]


# process a frame given by applying functions
def process(image):
    # get the coordinates for the mask
    height = image.shape[0]  # 1080
    width = image.shape[1]  # 1920

    p1 = [round(width * .20), round(height * .72)]
    p2 = [round(width * .40), round(height * .55)]
    p3 = [round(width * .60), round(height * .55)]
    p4 = [round(width * .80), round(height * .72)]

    # create a trapezoidal mask around the road
    mask_vertices = np.int32([p1, p2, p3, p4])

    screen_verts = np.float32([[0, height], [0, 0], [width, 0], [width, height]])

    # warp the frame to fit this trapezoidal mask to get a bird's-eye view of the road
    warped_img = warping(image, np.float32(mask_vertices), screen_verts)

    # convert the image into grayscale and use a bilateral filter on it
    gray = cv2.cvtColor(warped_img, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 11, 19, 19)

    # use canny edge filter on the grayscale image
    cannyed_image = cv2.Canny(gray, 200, 150, apertureSize=5)

    # crop the image into 2 seperate images, one of the left side of the road and one of the right
    crop_l = cannyed_image[0:height, round(width * 0.1):round(width * 0.3)]
    crop_r = cannyed_image[0:height, round(width * 0.7):round(width * 0.95)]

    # call the detect hough function to detect all the HoughLines in the frame
    # and return a list of the coordinates for each line
    lines_l = detect_hough(crop_l)
    lines_r = detect_hough(crop_r)

    # filter and check the HoughLines by distance to get 2 lines, then return the midline of those two lines
    final_l, mid_linel = check_hough(lines_l, warped_img, round(width * 0.1))
    final_r, mid_liner = check_hough(lines_r, warped_img, round(width * 0.7))

    global coord_l, coord_r

    # if no line has been detected, use the most recently stored coordinate in the list
    # that was initialized at the beginning of the program
    if len(mid_liner) == 0:
        mid_liner = coord_r[0]
        cv2.line(warped_img, mid_liner[0], mid_liner[1], (0, 0, 255), 50, cv2.LINE_AA)
    if len(mid_linel) == 0:
        mid_linel = coord_l[0]
        cv2.line(warped_img, mid_linel[0], mid_linel[1], (0, 0, 255), 50, cv2.LINE_AA)

    # pop the last coordinate pair used and append the current ones to the list
    coord_l.pop(0)
    coord_r.pop(0)
    coord_l.append(mid_linel)
    coord_r.append(mid_liner)

    # if lines have been detected for both sides,
    # average the two lines together and draw that middle line
    if len(mid_liner) > 1 and len(mid_linel) > 1:
        coords_mid = average_lines(mid_liner[0], mid_liner[1], mid_linel[0], mid_linel[1])
        cv2.line(warped_img, coords_mid[0], coords_mid[1], (255, 0, 0), 50)

    # unwarp the image with the unwarped function
    unwarped_img = unwarped(warped_img, np.float32(mask_vertices), screen_verts)

    # add the unwarped image and the orginal image ontop of each other
    finished = cv2.addWeighted(image, 0.5, unwarped_img, 0.5, 0.0)

    # detect the left and right arrows on this finished image
    detected_left = detect_arrow_left(finished)
    detected_right = detect_arrow_right(detected_left)

    # return the final image
    return detected_right

