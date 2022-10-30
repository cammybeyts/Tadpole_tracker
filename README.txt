This readme file was generated on [30-10-2022] by [Cammy Beyts]

GENERAL INFORMATION

Title of Tutorial: Tadpole tracking tutorial

Author Information
Name: Cammy Beyts
ORCID: 0000-0002-4729-2982
Institution: Edinburgh University
Address: The Roslin Institute and R(D)SVS, University of Edinburgh, Easter Bush, UK
Email: cammy.beyts@ed.ac.uk

About:

Tadpole tracker is an OpenCV based object tracking software run in python.  
The softwear is designed to track a single object (such as a tadpole) in a uniform environment.
Eg a tadpole housed in a stationary tank lit from below using a lightbox.

Requirements:

In order to use the tadpole tracker, you must install miniconda which will also install python 3 onto your operating system.
You will also need to install several python packages to allow the tracker to run. 
It is recommended that you run the python tracker in a "conda envoirnment" to prevent making changes to your main system
Links for how to install miniconda, set up a conda envoirnment and install python packages in these have been listed below:

1. Install miniconda
miniconda https://docs.conda.io/en/latest/miniconda.html

2. Conda envoirnment
create conda environment https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#creating-an-environment-with-commands
activate conda envoironment https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#activating-an-environment
deactivate conda environment https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#deactivating-an-environment

3. install python packages
activate your conda environment and run the following commands to install necessary python packages (brackets )
https://packaging.python.org/en/latest/tutorials/installing-packages/

pip 
numpy
pandas
scipy
os
opencv-python
imutils

Download tadpole tracker:

Go on the Tadpole Tracker GitHub page](https://github.com/cammybeyts/Tadpole_tracker) and Download the .zip file to your choice location on your computer, and unzip the folder.

The Tadpole Tracker is a python code which can be used to track the movement of a single tadpole from pre-recorded video footage. 
Some parameters need to be changed (eg location of video, size of object to be tracked ect).
The contents of the GitHub code has been displayed below:

__pycache__ : irrelevant

README.txt : this document 

Tracking_functions.py : All the functions for running the Tadpole Tracker are in this file but users do not need to modify this file.  The file is annotated to explain the different functions

Track_Tadpole.py : This is the file which you need to run to track tadoles from your video footage.  Some parameters will need to be changed in this file. 

ACT_video_info.txt : txt file containing information about the tadpoles and video files for tracking 

example_video : folder containing some example video files 

Tracking_files : folder where tracking results can be stored 

Running Tadpole Tracker 
In the instuctions below, the instructions are given for tracking tadpoles in the example videos provided. 

1a. Open the command line 
In the the command line terminal, navigate to the folder where the Tadpole Tracker was downloaded to from GitHub. 
Ensure that you are located in the folder containing Track_Tadpole.py

1b. Activate your virtual conda environment

1c. Open Track_Tadpole.py 
Using txt reader such as Visual Studio Code, open the Track_Tadpole.py
Lines 9-14 are parts of the code you may need to change to improve the performance of the tadpole tracker, but when first experimenting with the script, the current settings can be left as they are. 
When using the Tadpole Tracker with your own videos you will have to use trial and error to modify these parameters to fit the problem.
    Batch = Batch number and refers to the batch number in ACT_video_info.txt file.  The Batch number can be changed to select different videos in the ACT_video_info.txt file. 
    sub_varThreshold = the pixel threshold value which is used to determine what is a moving tadpole.  This value works best between 90-150. 
    sub_learn_rate = the rate at which the tracker learns what is a staionary vs moving object.  -1 is the default and works well - 0.05 also works well 
    blur_kernal = the number of pixels which are blured together to create a blured image used for tracking. Use a smaller kernal (1,1) for small tadpoles and a larger kernal (5,5) for bigger tadpoles 
    min_area = the min area in pixels which should be considered a tadpole - increase if small non-tadpole objects continue to be detected (eg specs of uneaten food)
    max_area = the max area in picels which should be considered a tadpole - decrease if larger objects (eg water ripples) contiue to be detected

line 22 the file name and location of the file containing the tadpole and video information
    ACT_vieo_info.txtcontents:
        Batch = Batch number - used to determine which video you want to track objects in. Currently, each video has a separate bacth number but if you want to run the tracker on several videos one after each other, the same batch number can be used for multiple lines.
        TadpoleID = Tadpole Identity
        Rep = Trial number 
        LR = left or right - Two tadpoles are filmed in separate tanks in one video, L or R, defines whether we are interested in the right or left tadpole. 
        video = location of video file 
        LXtop = x coordinate of top left hand tank 
        LYtop = y coordinate of top left hand tank 
        LXbottom = x coordinate of bottom left hand tank 
        LYbottom = y coordinate of bottom left hand tank 
        RXtop = x coordinate of top right hand tank 
        RYtop = y coordinate of top right hand tank 
        RXbottom = x coordinate of bottom right hand tank 
        RYbottom = y coordinate of bottom right hand tank

line 50 where you want to result files to be stored 
    currently result files will be stored in the folder Tacking_files/

1d. Run Track_Tadpole.py 
Execute the Tadpole Tracker code by running the following command in the command line terminal: python Track_Tadpole.py
When the Tadpole Tracker code is running, a new window will open showing the video file with a line tracking the object 
as it moves on the screen. 
There will also be a few bits of information (tadpoleID, trial number and distance travelled) displayed on the image. 
You may notice that Tadpole Tracker does not perform perfectly on all the videos, 
so you need to modify the parameters in lines 9-14 to solve the problem

1e. The result files 
After you have run the Tadpole Tracker, you can view the results file which will be located in the folder named Tracking_files/
The result file will be named with the assay name, TadpoleID name and trial number, information pulled from the Act_video_info.txt file. 
For example the first video is of a Activity assayt for Tadpole 649 in its first behavioural recording trail.  Therefore the result file name is ACT_649_1.txt
The result file will contain the Tadpole's name, its trial number, the total distance and culmative distance it swam in each frame of the video














