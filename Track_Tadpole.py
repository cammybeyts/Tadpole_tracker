import cv2
import os
import numpy as np
from collections import deque
import Tracking_functions as tc


#information to change 
Batch = "7"
sub_varThreshold = 150 #values usually work between 90-150 - the pixel threshold value to be counted as a "moving tadpole" object
sub_learn_rate = -1 # -1 is the default, 0.05 also works well
blur_kernal = (1,1) #use smaller kernal sizes (1,1) for small tadpoles and larger kernals (5,5) for big tadpoles
min_area = 100 #minimum area in pixels 
max_area = 900 #maximum area in pixels 

##create two numpy arrays to place over images
#NB pixel size is written as 360x640 in np but would be 640x360 in cv2
imgL = np.zeros((360, 640, 3), np.uint8) #create a numpy array 360x640 = pixel size of video
imgR  = np.zeros((360, 640, 3), np.uint8) #create a numpy array 360x640 = pixel size of video

#open and read the txt file of video names
myfile = open('/Users/cbeyts/Documents/Edinburgh_PhD_documents/Projects/Cleaned_tracking_code/ACT_video_info.txt', encoding="ISO-8859-1")
myfile = myfile.readlines() #read all the lines of this file
for line in myfile[1:]: #ignore header line
    line = line.strip() #removes unreadable characters from end of lines
    line = line.split() #ensures that lines are read line by line correctly
    BatchID = 0 #specify the column of batchnumbers
    if line[BatchID] != Batch: #if 'BatchID' is not equal to the 'Batch' number specified then ignore this line and continue
            continue
    TadpoleID = 1 #specify the column of tadpoleIDs
    TrialID = 2 #specify  the column of trial number per tadpoleID
    columnvid = 4 #specify the column containing the video directory location
    columnLR = 3 #specify the column which states if tadpole on left 'L' or right 'R'
    #next few columns specify the XY coordinates of the tadpole containers
    LXtop = 5 #L tadpole top left X
    LYtop = 6 #L tadpole top left y
    LXbottom = 7 #L tadpole bottom right x
    LYbottom = 8 #L tadpole bottom right y
    RXtop = 9 #R tadpole top left X
    RYtop = 10 #R tadpole top left Y
    RXbottom = 11 #R tadpole bottom right X
    RYbottom = 12 #R tadpole bottom left Y

    vidx = (line[columnvid]) #object "vid" refers to the column stating a video file's location
    colLR = (line[columnLR]) #oject "colLR" refers to the column stating if tadpole is on the left or the right
    rectL = cv2.rectangle(imgL, (int(line[LXtop]), int(line[LYtop])), (int(line[LXbottom]), int(line[LYbottom])), (255, 255, 255), -1) #object rectL defines the regtangle coordinates, colour and thickness of the tadpole containers located on the left
    rectR = cv2.rectangle(imgR, (int(line[RXtop]), int(line[RYtop])), (int(line[RXbottom]), int(line[RYbottom])), (255, 255, 255), -1) #object rectR defines the regtangle coordinates, colour and thickness of the tadpole containers located on the right
    
    ##set up the conditions required for the .txt files where the results will be stored
    results_fn = ('_'.join(('Tracking_files/ACT', line[TadpoleID], line[TrialID]))) #name file "file_location"/ACT_tadpoleID_trial according to cooresponding lines in inputted .txt file
    suffix = '.txt' #ensure that the file is of.txt type 
    results_txt = os.path.join(results_fn + suffix) #join the suffix onto the end of the results_fn file name
    myresults = open(results_txt, 'w') #open the results file.  "w" = Overwite any exsisting contents.
    printheader = print('TadpoleID', 'TrialID', 'FrameNo', 'Xcentroid', 'Ycentroid', 'DistX', 'DistY', 'PixelDist', 'CumulPixelDist', sep='\t', file=myresults) #print header lines in results file, separate each column by "\t"
    myresults.close() #close results file
    myresults = open(results_txt, 'a') 

    #set up a list to store a single x y point at a time. 
    prev_x = deque(maxlen=1) 
    prev_y = deque(maxlen=1)
    prev_xy = deque(maxlen=1)
    prev_x.append(0)
    prev_y.append(0)
    prev_xy.append(None)

    ##set up a series of lists to store values in for use later
    #list of points to follow detected object movement (contails) 
    pts = deque(maxlen=100) #maxlen = object location in previous x frames
    #list of points to calculate distance between consecutive cx and cy points
    cxpts = deque(maxlen=2) #maxlen = 2. Only hold current object X position and last object X position
    cypts = deque(maxlen=2) #maxlen = 2. Only hold current object Y position and last object Y position
    #set up list to calculate cumulative distance travelled:
    dist_travelled = deque() #hold all cumulative distance values calculated

    cap = cv2.VideoCapture(vidx) #object "cap".  Use cv2.videocapture to read the frames in a video
    fps = int(cap.get(cv2.CAP_PROP_FPS)) #determines number of frames per second in video
    cap.set(1,1)
    end_frame = int(600*fps) #end frame = 15mins in secs (60*15 = 900secs) * number of frames per second (fps)
    framecount = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) # object "framecount". count the number of frames in a video and convert into an integer

    ##Define the background subtraction method to be used
    sub_history = 100 #keep at 500 - how many prior frames are used to determine stationary objects
    subtractor = cv2.createBackgroundSubtractorMOG2(history=sub_history, varThreshold=sub_varThreshold, detectShadows=False) #object "subtractor". using the cv2.createBackgroundSubtractorMOG2 method

    while True:
        frame = cap.read() #for each frame, read from the video capture file
        frame = frame[1] #handle the frame from the video capture file
        frame_pos = cap.get(cv2.CAP_PROP_POS_FRAMES) #for each frame, print the frame number
        #If video is finished - break from the loop, otherwise continue
        if frame_pos > end_frame:
            myresults.close() #close the file when the video is finished
            break
        if frame is None:
            myresults.close() #close the file when the video is finished
            break
        if colLR == "R": 
           frame = cv2.bitwise_and(frame, rectR) #ROI = right tadpole
        if colLR == "L":
            frame = cv2.bitwise_and(frame, rectL) #ROI = left tadpole
        
        mask, blur, eq = tc.create_mask(frame, subtractor, sub_learn_rate, blur_kernal)

        c, cx, cy, cxcy = tc.detect_contours(frame, blur, mask, eq, min_area, max_area, prev_x, prev_y, prev_xy)
        print(cx, cy)
        ix, iy, Pixel_dist, cumul_dist_travelled = tc.calculate_distance(cx, cy, cxpts, cypts, dist_travelled)

        pts = tc.draw_lines(cxcy, pts, frame, blur, mask)

        printresults = print(line[TadpoleID], line[TrialID], int(frame_pos), cx, cy, ix, iy, Pixel_dist, cumul_dist_travelled, sep='\t', file=myresults) #print results to file
    
        frame, blur, mask, eq = tc.HUD_info(frame, blur, mask, eq, line, TadpoleID, frame_pos, cumul_dist_travelled)

        output = tc.output(frame, mask, blur, eq, mode="frame+new_mask")

        key = tc.frame_display_time(fps, mode="fast_speed")
        
        
        cv2.imshow('tadpole_tracker', frame)
                

        ##To skip a video press:
        if key == ord('q'):
            break
    
    #close files and windows after analysis is complete        
    cap.release() #release the video
    cv2.destroyAllWindows() #destroy any video windows open        
    myresults.close() #close the file when a video is finished or no more videos are playing