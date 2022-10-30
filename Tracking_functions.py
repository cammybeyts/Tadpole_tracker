import cv2
import imutils
import numpy as np
import math


def create_mask(frame, subtractor, sub_learn_rate, blur_kernal):
    """
    This function retrieves a video frame and preprocesses it for 
    object tracking. 
    The code converts the image to greyscale (gray, eq), blurs the image (blur) to reduce noise and returns 
    a thresholded image (mask) which is determined by a min and max threshold values (minthresh and maxthresh).
    The mask is dilated to remove small spots appearing in the mask. 

    Parameters
    ----------
    frame: ndarray, shape(n_rows, n_cols, 3)
        source image with 3 colour channels
    subtractor: cv2 function
        the type of subtractor used to create mask
    sub_learn_rate: float
        how many previous frames are used to estimate tadpole's next position
    blur_kernal: 
        array, int
        how many pixels are combined to create the blurred image
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    eq = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, blur_kernal, 0)
    mask = subtractor.apply(blur, learningRate=sub_learn_rate)
    minthresh = 60 
    maxthresh = 255 
    mask = cv2.threshold(mask, minthresh, maxthresh, cv2.THRESH_BINARY)[1] 
    mask = cv2.dilate(mask, None, iterations=3) 
    return mask, blur, eq

def detect_contours(frame, blur, mask, eq, min_area, max_area, prev_x, prev_y, prev_xy):
    """
    This function detects contours (binary mask images), thresholds them based on area and draws them.

    Parameters
    ----------
    frame: ndarray, shape(n_rows, n_cols, 3)
        source image with 3 colour channels
    blur: ndarray, shape(n_rows, n_cols, 1)
        blurred image with 1 colour channel
    mask: ndarray, shape(n_rows, n_cols, 1)
        binarised image with 1 colour channel 
    eq: ndarray, shape(n_rows, n_cols, 1)
        source image converted from colour to grey - 1 colour channel
    min_area: int
        the minimum area a contour should be to considered a tadpole and not noise eg specs of food left in tank 
    max_area:
        the minimum area a contour should be to considered a tadpole and not noise eg water ripples
    prev_x: int
        previous x contour coordinate
    prev_y: int
        previous y contour coordinate
    prev_xy: array, int
        previous xy contour coordinate

    """
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE) #finds the contours (outlines) of the binary mask image
    cnts = imutils.grab_contours(cnts) #select these contour
    for c in cnts:
        area = cv2.contourArea(c)
        (x, y, w, h) = cv2.boundingRect(c)
        extent = area / float(w * h)
        
        if area < min_area or area > max_area:
            cv2.drawContours(mask, [c], -1, 0, -1)
    mask = cv2.bitwise_and(mask, mask, mask = mask)
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE) #finds the contours (outlines) of the binary mask image
    cnts = imutils.grab_contours(cnts) #select these contour
    for c in cnts:
        c = sorted(cnts, key = cv2.contourArea, reverse=True)[-1] 
        M = cv2.moments(c) #allows calculation of centroid
        if M["m00"] or M["m10"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            cxcy = (int(M['m10']/M['m00']), int(M['m01']/M['m00'])) 
        else:
            cx = 0
            cy = 0
            cxcy = (0,0)
        if cx == 319 and cy == 179:
            cx = 0
            cy = 0
            cxcy = (319,179)
        prev_x.appendleft(cx)
        prev_y.appendleft(cy)
        prev_xy.appendleft(cxcy)
        (cx, cy, w, h) = cv2.boundingRect(c) #Define the xy coordinates and width+height of the contour
        for img in (frame, blur, mask, eq):
            cv2.rectangle(img, (cx, cy), (cx + w, cy + h), (0, 255, 0), 1) #define colour and shape of rectangle and place on the frame
    else:
        for x in prev_x:
            cx = x
        for y in prev_y:
            cy = y
        for xy in prev_xy:
            cxcy = xy
        c = None
    return c, cx, cy, cxcy

def calculate_distance(cx, cy, cxpts, cypts, dist_travelled):
    """
    This function calculates the distance the tracked object moves.
    The distance is calculated for consecutive and cumlative distance travelled. 

    Parameters
    ----------
    cx: float
        The objets current location on the x axsis (its x centroid) in current frame
    cy: float
        The objets current location on the y axsis (its y centroid) in current frame
    cxpts: array, float
        A list of all current x centroids from previous frames
    cypts: array, float
        A list of all current y centroids from previous frames
    dist_travelled: float
        distance object has moved from this frame and previous frame
    """
    #step 1: append xy coordinates to a list
    cxpts.appendleft(cx) #append x coordinates to cxpts list
    cypts.appendleft(cy) #append y coordinates to cxpts list
        
    #step 2: calculate distance between consecutive x and y points 
    #calculate the distance between consecutive x points and call the value ix
    ix = 0 #unless otherwise stated ix = 0
    for ix in range(1, len(cxpts)): #for values in the cxpts list
        if cxpts[ix] == 0 or cxpts[ix-1] == 0: #if the current cx value is a zero, ix = 0
            ix = 0
        else: #otherwise perform the following to calculate ix
            ix = (cxpts[ix]-cxpts[ix-1]) #ix = current cx value - previous cx value
    #calculate distance between consecutive y points
    iy = 0 #unless otherwise stated iy = 0
    for iy in range(1, len(cypts)): #for values in the cypts list
        if cypts[iy] == 0 or cypts[iy-1] == 0: #if the current cy value is a zero, iy = 0
            iy = 0
        else: #otherwise perform the following to calculate iy
            iy = (cypts[iy]-cypts[iy-1]) #iy = current cy value - previous cy value

    #step 3: calculate the distance travelled between consecutive points
    #calculate distance travelled between two points (in pixels)
    #define some values
    square_ix = (ix*ix) 
    square_iy = (iy*iy) 
    #calculate the distance as sqrt of the square_ix + square_iy values
    Pixel_dist = math.sqrt(square_ix+square_iy) 
    #round the value to 2 decimal places
    Pixel_dist = round(Pixel_dist, 2)

    #step 4: calculate cumlative distance travelled (in pixels)
    #append distance travelled calcultions to a list
    dist_travelled.appendleft(Pixel_dist)
    #unless otherwise stated cumlative distance travelled = 0
    cumul_dist_travelled = 0
    #sum each value found in the dist_travelled list
    for cumul_dist_travelled in range(1, len(dist_travelled)):
        cumul_dist_travelled = sum(dist_travelled)
    #round the value to 2 decimal places
    cumul_dist_travelled = round(cumul_dist_travelled, 2)

    return ix, iy, Pixel_dist, cumul_dist_travelled

def draw_lines(cxcy, pts, frame, blur, mask):
    """
    This function draws a line between consecutive location the object moves
    
    Parameters
    ----------
    cxcy: array, float
        The objets current location (its centroid) in current frame
    pts: int
        The number of previous consecutive locations to draw lines for
    frame: ndarray, shape(n_rows, n_cols, 3)
        source image with 3 colour channels
    blur: ndarray, shape(n_rows, n_cols, 1)
        blurred image with 1 colour channel
    mask: ndarray, shape(n_rows, n_cols, 1)
        binarised image with 1 colour channel 
    """
    if cxcy != (319,179):
        pts.appendleft(cxcy)
    for i in range(1, len(pts)):
            if pts[i - 1] is None or pts[i] is None:
                continue
            line_thickness = 1
            for img in (frame, blur, mask):
                cv2.line(img, pts[i - 1], pts[i], (0, 0, 255), line_thickness) #place centroid lines on frame
                cv2.line(img, pts[i - 1], pts[i], (0, 0, 255), line_thickness) #place centroid lines on mask image
    return pts

def HUD_info(frame, blur, mask, eq, line, columnID, frame_pos, cumul_dist_travelled):
    """
    This function provides the Heads UP Display on the image to show details of the current tadpole being tracked
    Parameters
    ----------
    frame: ndarray, shape(n_rows, n_cols, 3)
        source image with 3 colour channels
    blur: ndarray, shape(n_rows, n_cols, 1)
        blurred image with 1 colour channel
    mask: ndarray, shape(n_rows, n_cols, 1)
        binarised image with 1 colour channel 
    eq: ndarray, shape(n_rows, n_cols, 1)
        source image converted from colour to grey - 1 colour channel
    line: str
        reads the information in the correct ACT_video_info.txt file
    columnID: str 
        gets tadpole ID from ACT_video_info.txt file under the column name ID
    frame_pos: int
        the current frame number of source image
    cumul_dist_travelled: float
        the total distance travelled object has been recorded to move in pixels
    """
    for img in (frame, blur, mask):
        cv2.rectangle(frame, (10, 225), (110,240), (255,255,255), -1) #rectangle location and colour
        cv2.putText(frame, "TadpoleID: {}".format(line[columnID]), (15, 235), cv2.FONT_HERSHEY_SIMPLEX, 0.35 , (0,0,0)) #retrieve frame number from cap and place in rectangle
        cv2.rectangle(frame, (10, 250), (110,265), (255,255,255), -1) #rectangle location and colour
        cv2.putText(frame, "Frame No: {}".format(int(frame_pos)), (15, 260), cv2.FONT_HERSHEY_SIMPLEX, 0.35 , (0,0,0)) #retrieve frame number from cap and place in rectangle
        cv2.rectangle(frame, (10, 275), (135,290), (255,255,255), -1) #rectangle location and colour for frame number
        cv2.putText(frame, "Dist (pixels): {}".format(cumul_dist_travelled), (15, 285), cv2.FONT_HERSHEY_SIMPLEX, 0.35 , (0,0,0)) #retrieve frame number from cap and place in rectangle
    
    return frame, blur, mask, eq

def output(frame, mask, eq, blur, mode="frame"):
    """
    This function provides different ways of viewing the output of the tracked object
    
    Parameters
    ----------
    frame: ndarray, shape(n_rows, n_cols, 3)
        source image with 3 colour channels
    blur: ndarray, shape(n_rows, n_cols, 1)
        blurred image with 1 colour channel
    mask: ndarray, shape(n_rows, n_cols, 1)
        binarised image with 1 colour channel 
    eq: ndarray, shape(n_rows, n_cols, 1)
        source image converted from colour to grey - 1 colour channel
    mode: str
        choose from 
            "frame" : shows tracked object in source image
            "mask" : shows tracked object in binarised mask image
            "blur" : shows tracked object in blurred image
            "frame+mask" : shows tracked object in source image and binarised mask image
            "frame_blur" : shows tracked object in source image and blurred image
            "blur+eq" : shows tracked object in blurred image and greyscale image
        different modes are useful when diagnosing problems with tracker
    """
    if mode == "frame":
        cv2.imshow('output', frame) 
    if mode == "mask":
        cv2.imshow('output', mask) 
    if mode == "blur":
        cv2.imshow('output', blur)
    if mode == "frame+mask":
        frame_plus_mask = cv2.bitwise_and(frame, frame, mask=mask)
        hstack_frame_plus_mask = np.hstack((frame, frame_plus_mask))
        cv2.imshow("output", hstack_frame_plus_mask)
    if mode == "frame_blur":
        blur_2_colour = cv2.cvtColor(blur, cv2.COLOR_GRAY2BGR)
        hstack_frame_blur = np.hstack((frame, blur_2_colour))
        cv2.imshow('output', hstack_frame_blur)
    if mode == "blur+eq":
        hstack_gray_plus_eq = np.hstack((blur, eq))
        cv2.imshow("output", hstack_gray_plus_eq)


def frame_display_time(fps, mode = "nat_speed"):
    """
    This function provides ways of changing the speed of different images
    
    Parameters
    ----------
    fps: int
        The number of frames per second the output is displayed
    mode: str
        choose from
            "nat_speed" : natural filming speed of 25 frames per second (1000ms / 25frames = each frame displayed for 40ms)
            "veryfast_speed" :  each frame displayed for 2ms = 40ms/20
            "fast_speed" : each frame displayed for 4ms = 40ms/10
            "med_speed" : each frame displayed for 4ms = 8ms/5
            "slow_speed" : each frame dispayed for 200ms = 40ms*5
        useful for when wanting to speed up or slow down tracking process

    """
    nat_speed = int(1000/fps) 
    veryfast_speed = int((1000/fps)/20) 
    fast_speed = int((1000/fps)/10) 
    med_speed = int((1000/fps)/5) 
    slow_speed = int((1000/fps)*5)
    if mode == "nat_speed":
        key = cv2.waitKey(nat_speed) & 0xFF
    if mode == "veryfast_speed":
        key = cv2.waitKey(veryfast_speed) & 0xFF
    if mode == "fast_speed":
        key = cv2.waitKey(fast_speed) & 0xFF
    if mode == "med_speed":
        key = cv2.waitKey(med_speed) & 0xFF
    if mode == "slow_speed":
        key = cv2.waitKey(slow_speed) & 0xFF
    return key


    


    



        
        