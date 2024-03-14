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

    chroma_img = chroma_key(warped_img)

    gray_image = cv2.cvtColor(chroma_img, cv2.COLOR_RGB2GRAY)

    # filtered_img = filters(warped_img)

    cv2.polylines(image, np.array([[p1, p2, p3, p4]], np.int32), True, (0, 255, 0), 8)

    crop_l = gray_image[0:width // 2, 0:height]
    cv2.imshow("crop", crop_l)
    crop_r = gray_image[width // 2:width, 0:height]

    lines = cv2.HoughLines(crop_l, 1, np.pi / 180, 50)

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
    # detect_r = detect_hough(crop_r)
    # print(detect_r)

    if len(line_coords) > 0:
        # print("hi")
        cv2.line(warped_img, line_coords[0][0], line_coords[0][1], (0, 0, 255), 8)
        # cv2.line(warped_img, detect_r[0][0], detect_r[0][1], (255, 0, 0), 8)

    # # apply the mask onto the given frame23456u
    # cropped_image = masking(filtered_img, np.array([mask_vertices], np.int32))
    #
    # cv2.imshow("masked", cropped_image)
    return warped_img
