# import the filter file functions
from filters import *


# process a frame given by applying functions
def process(image):
    # get the coordinates for the mask
    height = image.shape[0]  # 1080
    width = image.shape[1]  # 1920

    p1 = [round(width / 4.4), height]
    p2 = [round(width / 2.3), round(height / 1.5)]
    p3 = [round(width / 1.8), round(height / 1.5)]
    p4 = [round(width / 1.3), round(height)]

    mask_vertices = np.int32([p1, p2, p3, p4])
    mask_reshaped = mask_vertices.reshape((-1, 1, 2))
    # cv2.polylines(image, [mask_reshaped], True, (0, 255, 255), 8)

    cv2.imshow('og', image)

    og_verts = np.float32([[0, height], [0, 0], [width, 0], [width, height]])

    warped_img, pers_matrix = warping(image, np.float32(mask_reshaped), og_verts)

    yellow = detect_yellow(warped_img)
    white = detect_white(warped_img)

    colored_img = yellow + white
    cv2.imshow("color", colored_img)

    # apply the filters onto the given frame
    filtered_img = filters(colored_img)
    cv2.imshow("filter", filtered_img)

    crop_l = filtered_img[0:height, 0:round(width * 0.3)]
    crop_r = filtered_img[0:height, round(width * 0.6):width]
    cv2.imshow("cropL", crop_l)
    cv2.imshow("cropR", crop_r)

    final_l, image_l = None, None
    final_r, image_r = None, None

    try:
        final_l, image_l = contouring(crop_l, warped_img)
        final_r, image_r = contouring(crop_r, warped_img, round(width * 0.6))
    except:
        pass

    lines_l = None
    lines_r = None

    if final_l is not None:
        cv2.imshow("final l", image_l)
        lines_l = detect_hough(image_l)

    if final_r is not None:
        cv2.imshow("final r", final_r)
        lines_r = detect_hough(image_r)

    if lines_l is not None:
        for i in lines_l:
            cv2.line(warped_img, i[0], i[1], (0, 255, 255), 8)
    if lines_r is not None:
        for i in lines_r:
            cv2.line(warped_img, i[0], i[1], (0, 255, 255), 8)

    return image
