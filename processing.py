# import the filter file functions
from filters import *


# process a frame given by applying functions
def process(image):
    # get the coordinates for the mask
    height = image.shape[0]  # 1080
    width = image.shape[1]  # 1920

    p1 = [round(width * .20), round(height * .72)]
    p2 = [round(width * .40), round(height * .55)]
    p3 = [round(width * .60), round(height * .55)]
    p4 = [round(width * .80), round(height * .72)]

    mask_vertices = np.int32([p1, p2, p3, p4])
    # cv2.polylines(image, [mask_vertices], True, (0, 255, 255), 8)

    # cv2.imshow('og', image)

    screen_verts = np.float32([[0, height], [0, 0], [width, 0], [width, height]])

    warped_img = warping(image, np.float32(mask_vertices), screen_verts)

    gray = cv2.cvtColor(warped_img, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 11, 19, 19)
    cannyed_image = cv2.Canny(gray, 200, 150, apertureSize=5)

    # yellow = detect_yellow(warped_img)
    # white = detect_white(warped_img)
    #
    # colored_img = yellow + white
    # cv2.imshow("color", colored_img)

    # apply the filters onto the given frame

    crop_l = cannyed_image[0:height, round(width * 0.1):round(width * 0.3)]
    crop_r = cannyed_image[0:height, round(width * 0.7):round(width * 0.95)]
    # cv2.imshow("cropL", crop_l)
    # cv2.imshow("cropR", crop_r)

    lines_l = None
    lines_r = None

    if crop_l is not None:
        # cv2.imshow("final l", crop_l)
        lines_l = detect_hough(crop_l)

    if crop_r is not None:
        # cv2.imshow("final r", crop_r)
        lines_r = detect_hough(crop_r)

    # if lines_l is not None:
    #     for i in lines_l:
    #         cv2.line(warped_img, i[0], i[1], (0, 255, 255), 10)
    # if lines_r is not None:
    #     for i in lines_r:
    #         cv2.line(warped_img, (i[0][0] + round(width * 0.7), i[0][1]),
    #                  (i[1][0] + round(width * 0.7), i[1][1]), (0, 255, 255), 10)

    # check to make sure slopes are the same

    heightw, widthw = warped_img.shape[:2]

    final_l, mid_linel = check_hough(lines_l, crop_l, warped_img, round(width * 0.1))
    final_r, mid_liner = check_hough(lines_r, crop_r, warped_img, round(width * 0.7))

    if len(mid_linel) > 1 and len(mid_liner) > 1:
        top_yr = min(mid_liner[0][1], mid_liner[1][1])
        if top_yr == mid_liner[0][1]:
            startr = mid_liner[0]
        else:
            startr = mid_liner[1]

        top_yl = min(mid_linel[0][1], mid_linel[1][1])
        if top_yl == mid_linel[0][1]:
            startl = mid_linel[0]
        else:
            startl = mid_linel[1]

        mid_liner.remove(startr)
        endr = mid_liner[0]
        mid_linel.remove(startl)
        endl = mid_liner[0]

        start_mid = (round((startr[0] + startl[0]) / 2), round((startr[1] + startl[1]) / 2))
        end_mid = (round((endr[0] + endl[0]) / 2), round((endr[1] + endl[1]) / 2))
        # cv2.line(warped_img, start_mid, end_mid, (0, 255, 255), 30)

    unwarped_img = unwarped(warped_img, np.float32(mask_vertices), screen_verts)

    #return cv2.add(image, unwarped_img)
    finished = cv2.addWeighted(image, 0.5, unwarped_img, 0.5, 0.0)
    # finished = detect_arrow_right(finished)
    # detected_left = detect_arrow_left(finished)
    # if detected_left:
    #     cv2.putText(finished, "left", (50, 75), fontFace=1, fontScale=5.0, color=(0, 0, 0), thickness=8)
    #     # hold for like 10 sec
    return finished
