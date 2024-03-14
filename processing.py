# import the filter file functions
from filters import *


# process a frame given by applying functions
def process(image):
    # get the coordinates for the mask
    height = image.shape[0]  # 1080
    width = image.shape[1]  # 1920

    p1 = [round(width / 4.2), height]
    p2 = [round(width / 2.3), round(height / 1.4)]
    p3 = [round(width / 1.7), round(height / 1.4)]
    p4 = [round(width / 1.3), round(height)]

    mask_vertices = np.float32([p1, p2, p3, p4])
    mask_reshaped = mask_vertices.reshape((-1, 1, 2))

    og_verts = np.float32([[0, height], [0, 0], [width, 0], [width, height]])

    # apply the filters onto the given frame
    # filtered_img = filters(image)

    warped_img = warping(image, mask_reshaped, og_verts)

    chroma_img = detect_white_yellow(warped_img)

    gray_image = cv2.cvtColor(chroma_img, cv2.COLOR_RGB2GRAY)

    # filtered_img = filters(warped_img)

    cv2.polylines(image, np.array([[p1, p2, p3, p4]], np.int32), True, (0, 255, 0), 8)

    crop_l = gray_image[0:height, width//8:width // 3]
    crop_r = gray_image[0:height, round(width*0.6):round(width*0.9)]
    cv2.imshow("crop", crop_r)

    # find the contours on the image
    contours, hierarchy = cv2.findContours(crop_r, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # contours = imutils.grab_contours((contours, hierarchy))

    # sort the list of contours by the contour area
    new = list(contours)
    new.sort(key=cv2.contourArea)

    # if there are at least 2 contours that have been detected
    if len(new) > 1:
        # get the 2 largest contours
        c1 = new[-1]
        c2 = new[-2]

        # fit polylines to each contour
        outline1 = cv2.approxPolyDP(c1, 4, True)
        cv2.drawContours(image, [outline1], -1, (0, 255, 255), 15)

        outline2 = cv2.approxPolyDP(c2, 4, True)
        cv2.drawContours(image, [outline2], -1, (0, 255, 255), 15)

        c1x1 = 0
        c1y1 = 0
        c1x2 = 0
        c1y2 = 0

        try:
            M1 = cv2.moments(c1)
            c1x1 = int(M1['m10']/M1['m00']) + round(width*0.6)
            c1y1 = int(M1['m01'] / M1['m00'])

            M2 = cv2.moments(c2)
            c1x2 = int(M2['m10'] / M2['m00']) + round(width*0.6)
            c1y2 = int(M2['m01'] / M2['m00'])
        except Exception as e:
            print(e)

        cv2.circle(warped_img, (c1x1, c1y1), 1, (0, 0, 255), 5)
        cv2.circle(warped_img, (c1x2, c1y2), 1, (255, 0, 0), 5)

        # # draw a midline by going through the polyline and averaging each x and y coordinate
        # # append this averaged coordinate to a list and turn that list into a numpy array
        # midline = []
        #
        # for pt1, pt2 in zip(outline1[:int(len(outline1) / 1.8)], outline2[:int(len(outline2) / 1.8)]):
        #     mid_x = int((pt1[0][0] + pt2[0][0]) / 2)
        #     mid_y = int((pt1[0][1] + pt2[0][1]) / 2)
        #     midline.append([[mid_x, mid_y]])

        # midline = np.array(midline, dtype=np.int32)

        # # draw a polyline from the numpy array onto the frame
        # cv2.polylines(image, [midline], False, (0, 255, 0), 15)


    # # apply the mask onto the given frame23456u
    # cropped_image = masking(filtered_img, np.array([mask_vertices], np.int32))
    #
    # cv2.imshow("masked", cropped_image)
    return warped_img
