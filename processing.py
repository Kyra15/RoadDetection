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

    yellow = detect_yellow(warped_img)
    white = detect_white(warped_img)

    colored_img = yellow + white
    cv2.imshow("color", colored_img)

    gray_image = cv2.cvtColor(colored_img, cv2.COLOR_RGB2GRAY)

    # filtered_img = filters(warped_img)

    cv2.polylines(image, np.array([[p1, p2, p3, p4]], np.int32), True, (0, 255, 0), 8)

    crop_l = gray_image[0:height, 0:round(width*0.3)]
    crop_r = gray_image[0:height, round(width*0.6):width]
    cv2.imshow("cropL", crop_l)
    cv2.imshow("cropR", crop_r)

    contouring(crop_l, warped_img)
    contouring(crop_r, warped_img, round(width*0.6))


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
