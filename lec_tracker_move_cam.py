#!/usr/bin/python

#Import the OpenCV and dlib libraries
import cv2
import dlib
import time
from timeit import default_timer as timer
from Naked.toolshed.shell import execute_js
from Naked.toolshed.shell import muterun_js
#Initialize a face cascade using the frontal face haar cascade provided with
#the OpenCV library , use upperbody haar cascade to target upper body.

#faceCascade = cv2.CascadeClassifier('haarcascade_upperbody.xml')
faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
#faceCascade = cv2.CascadeClassifier('haarcascade_fullbody.xml')

#The deisred output width and height
OUTPUT_SIZE_WIDTH = 775
OUTPUT_SIZE_HEIGHT = 600

def detectAndTrackLargestFace():
    #Open the ip ptz camera
    #capture = cv2.VideoCapture('rtsp://admin:@192.168.1.110:554/1/h264major latency=0')
    capture = cv2.VideoCapture('rtsp://192.168.1.110:554/1/h264major')
	#if need to use web-cam use the 0 option
    #capture = cv2.VideoCapture(0)

    #Create two opencv named windows
    cv2.namedWindow("base-image", cv2.WINDOW_AUTOSIZE)
    cv2.namedWindow("result-image", cv2.WINDOW_AUTOSIZE)

    #Position the windows next to eachother
    cv2.moveWindow("base-image",0,100)
    cv2.moveWindow("result-image",400,100)

    #Start the window thread for the two windows we are using
    cv2.startWindowThread()

    #Create the tracker we will use
    tracker = dlib.correlation_tracker()

    #The variable we use to keep track of the fact whether we are
    #currently using the dlib tracker
    trackingFace = 0

    #The color of the rectangle we draw around the tracking object face or upper body
    rectangleColor = (78,0,137)

    try:
        current_x = 0
        count = 2
        focused = True
        center_coords = 180
        max_error = 0
        h_error = 0
        custom_tracker = False
        no_rot_in_progress = False
        custom_sync = True
        start_timer = None
        custom_sync_main = True
        custom_sync_vertical = True
        start_timer_v = None
        time_required = 0
        start_tl = None
        check_vertical = False
        time_required_v = 0
        while True:
            #Retrieve the latest image from the ip-cam / webcam
            rc,fullSizeBaseImage = capture.read()

            #Resize the image to 320x240
            baseImage = cv2.resize( fullSizeBaseImage, ( 320, 240))

            #Check if a key was pressed and if it was Q, then destroy all
            #opencv windows and exit the application
            pressedKey = cv2.waitKey(2)
            if pressedKey == ord('Q'):
                cv2.destroyAllWindows()
                exit(0)

            #Result image is the image we will show the user, which is a
            #combination of the original image from the ip-cam / webcam and the
            #overlayed rectangle for the largest face
            resultImage = baseImage.copy()

            #If we are not tracking a face, then try to detect one
            if not trackingFace:

                #For the face detection, we need to make use of a gray
                #colored image so we will convert the baseImage to a
                #gray-based image
                gray = cv2.cvtColor(baseImage, cv2.COLOR_BGR2GRAY)
                #Now use the haar cascade detector to find all faces
                #in the image
                faces = faceCascade.detectMultiScale(gray, 1.3, 5)

                #print("Using the cascade detector to detect face")


                #we are only interested in the 'largest'
                #face in order to detect lecturer, and we determine 
				#this based on the largest
                #area of the found rectangle. First initialize the
                #required variables to 0
                maxArea = 0
                x = 0
                y = 0
                w = 0
                h = 0

                #Loop over all faces and check if the area for this
                #face is the largest so far
                #We need to convert it to int here because of the
                #requirement of the dlib tracker. If we omit the cast to
                #int here, you will get cast errors since the detector
                #returns numpy.int32 and the tracker requires an int
                for (_x,_y,_w,_h) in faces:
                    if _w*_h > maxArea:
                        x = int(_x)
                        y = int(_y)
                        w = int(_w)
                        h = int(_h)
                        maxArea = w*h

                #If one or more faces are found, initialize the tracker
                #on the largest face in the picture
                if maxArea > 0 :

                    #Initialize the tracker
                    tracker.start_track(baseImage,
                                        dlib.rectangle( x-10,
                                                        y-20,
                                                        x+w+10,
                                                        y+h+20))

                    #Set the indicator variable such that we know the
                    #tracker is tracking a region in the image
                    trackingFace = 1

            #Check if the tracker is actively tracking a region in the image
            if trackingFace:

                #Update the tracker and request information about the
                #quality of the tracking update
                trackingQuality = tracker.update( baseImage )

                #If the tracking quality is good enough, determine the
                #updated position of the tracked region and draw the
                #rectangle
                if trackingQuality >= 8.75:
                    #print("Detected Face")
                    start_tl = None
                    tracked_position =  tracker.get_position()

                    t_x = int(tracked_position.left())
                    t_y = int(tracked_position.top())
                    t_w = int(tracked_position.width())
                    t_h = int(tracked_position.height())
                    cv2.rectangle(resultImage, (t_x, t_y),
                                                (t_x + t_w , t_y + t_h),
                                                rectangleColor ,2)
                    # if count>1:
                    #    current_x = t_x
                    #    count-=1

                    #print("Coordinates : " + str(t_x) + ", "+ str(t_y) + ", "+ str(t_h) + ", "+ str(t_w))
                    #print("rec : " + str(t_x) + ", "+ str(t_y) + ", "+ str(t_x + t_w) + ", "+ str(t_y + t_h))
                    #print("Center Coordinates : " + str(t_w/2) + ", "+ str(t_h/2))

                    #max_error = 5

                    # vm_cd = int(t_x)
                    # if current_x<180 and focused:
                    #    rot_cen = (180-current_x)*22
                    #    print('rotation time required ' + str(rot_cen))
                    #    turn_left_ptz = execute_js('onvif_movement/turn_left.js',str(rot_cen))
                    #    if turn_left_ptz:
                    #        print('Focused Success - Turned Left')
                    #        focused = False
                    #        custom_tracker = True
                    #        no_rot_in_progress = True
                    #    else:
                    #        print('failed left')
                    # if current_x>180 and focused:
                    #    rot_cen = (current_x-180)*22
                    #    print('rotation time required ' + str(rot_cen))
                    #    turn_right_ptz = execute_js('onvif_movement/turn_right.js ',str(rot_cen))
                    #    if turn_right_ptz:
                    #        print('Focused Success - Turned Right')
                    #        focused = False
                    #        custom_tracker = True
                    #        no_rot_in_progress = True
                    #    else:
                    #        print('failed right')

                    custom_tracker = True #True
                    no_rot_in_progress = True
                    current_pos = t_x
                    h_error = abs(180 - current_pos)
                    #print('h_error ' + str(h_error))

                    if custom_tracker and h_error > 40:
                        print('Distance found! ' + str(h_error))
                        check_vertical = False
                        if custom_sync_main:
                            print('Tracker Standby')
                            if current_pos < 140:
                                no_rot_in_progress = False
                                #rot_cen = (180 - current_pos) * 22
                                rot_cen = abs((130 - t_x) * 11)
                                print('Rotation Time Required ' + str(rot_cen))

                                if start_timer is None:
                                    start_timer = timer()

                                turn_left_ptz = muterun_js('onvif_movement/turn_left.js', str(rot_cen))

                                custom_sync = True
                                rot_cen_in_sec = int(rot_cen / 1000)
                                time_required = rot_cen_in_sec + 2

                                end_timer = timer()
                                timer_diff = int(end_timer - start_timer)

                                if timer_diff >= time_required:
                                    custom_sync = True
                                else:
                                    custom_sync = False

                                if custom_sync:
                                    start_timer = None
                                    custom_sync_main = True
                                else:
                                    custom_sync_main = False

                                if turn_left_ptz.exitcode == 0:
                                    print('Custom Tracker - Turned Left')
                                    no_rot_in_progress = True
                                    #print(response.stdout)
                                else:
                                    print('failed left')
                                    #sys.stderr.write(response.stderr)

                            if current_pos > 220:
                                no_rot_in_progress = False
                                #rot_cen = (180 - current_pos) * 22
                                rot_cen = abs((130 - t_x) * 11)
                                print('Rotation Time Required ' + str(rot_cen))

                                if start_timer is None:
                                    start_timer = timer()

                                turn_left_ptz = muterun_js('onvif_movement/turn_right.js', str(rot_cen))

                                custom_sync = True
                                rot_cen_in_sec = int(rot_cen / 1000)
                                time_required = rot_cen_in_sec + 2

                                end_timer = timer()
                                timer_diff = int(end_timer - start_timer)

                                if timer_diff >= time_required:
                                    custom_sync = True
                                else:
                                    custom_sync = False

                                if custom_sync:
                                    start_timer = None
                                    custom_sync_main = True
                                else:
                                    custom_sync_main = False

                                if turn_left_ptz.exitcode == 0:
                                    print('Custom Tracker - Turned Right')
                                    no_rot_in_progress = True
                                    # print(response.stdout)
                                else:
                                    print('failed right')

                        else:
                            print('Tracker Waiting!')
                            #custom_tracker = False

                            end_timer = timer()
                            timer_diff = int(end_timer - start_timer)

                            if timer_diff >= time_required:
                                custom_sync = True
                            else:
                                custom_sync = False

                            if custom_sync:
                                start_timer = None
                                custom_sync_main = True
                            else:
                                custom_sync_main = False
                    else:
                        print('Lecturer Horizontal Distance Under Control! ' + str(h_error))
                        check_vertical = True

                    # vertical tracker controller
                    current_pos_vertical = t_y
                    v_error = abs(63 - current_pos_vertical)
                    if check_vertical and custom_sync_vertical and v_error > 22:
                        print('Vertical Distance Found! ' + str(v_error))
                        rot_cen_vertical = abs((63 - current_pos_vertical) * 12)
                        print('Vertical Rotation Time Required ' + str(rot_cen_vertical))
                        if current_pos_vertical < 40:
                            #print('Need to move down - script up')
                            if start_timer_v is None:
                                start_timer_v = timer()

                            turn_down_ptz = muterun_js('onvif_movement/turn_up.js', str(rot_cen_vertical))

                            rot_cen_v_in_sec = int(rot_cen_vertical / 1000)
                            time_required_v = rot_cen_v_in_sec + 2

                            end_timer_v = timer()
                            timer_diff_v = int(end_timer_v - start_timer_v)

                            if timer_diff_v >= time_required_v:
                                start_timer_v = None
                                custom_sync_vertical = True
                            else:
                                custom_sync_vertical = False

                            if turn_down_ptz.exitcode == 0:
                                print('Vertical Tracker - Turned Down')
                            else:
                                print('failed down')

                        if current_pos_vertical > 85:
                            #print('Need to move up script down')
                            if start_timer_v is None:
                                start_timer_v = timer()

                            turn_down_ptz = muterun_js('onvif_movement/turn_down.js', str(rot_cen_vertical))

                            rot_cen_v_in_sec = int(rot_cen_vertical / 1000)
                            time_required_v = rot_cen_v_in_sec + 2

                            end_timer_v = timer()
                            timer_diff_v = int(end_timer_v - start_timer_v)

                            if timer_diff_v >= time_required_v:
                                start_timer_v = None
                                custom_sync_vertical = True
                            else:
                                custom_sync_vertical = False

                            if turn_down_ptz.exitcode == 0:
                                print('Vertical Tracker - Turned Up')
                            else:
                                print('failed up')
                    else:
                        print('Lecturer Vertical Distance Under Control! ' + str(v_error))
                        #print('check vert ' + str(check_vertical))
                        #print('check custom_sync_main ' + str(custom_sync_main))
                        #print('check custom_sync_vertical ' + str(custom_sync_vertical))
                        #if check_vertical and custom_sync_main and not custom_sync_vertical:
                        if check_vertical and not custom_sync_vertical:
                            print('unlocked vertical locked within')
                            # custom_sync_vertical = True
                            end_timer_v = timer()
                            timer_diff_v = int(end_timer_v - start_timer_v)

                            if timer_diff_v >= time_required_v:
                                start_timer_v = None
                                custom_sync_vertical = True
                            else:
                                custom_sync_vertical = False

                        #print (custom_sync_vertical)

                    # print('v_error ' + str(current_pos_vertical))

                    # end of vertical tracker

                else:
                    #If the quality of the tracking update is not
                    #sufficient (e.g. the tracked region moved out of the
                    #screen) we stop the tracking of the face and in the
                    #next loop we will find the largest face in the image
                    #again
                    trackingFace = 0
                    print("Tracking Lost")

            else:
                if start_tl is None:
                    start_tl = time.time()
                end_tl = time.time()
                diff_tl = abs(end_tl - start_tl)
                # wait for 10 seconds
                if diff_tl >= 10:
                    print('Camera will be Recalibrated!')
                    recalibrate_ptz = execute_js('onvif_movement/recal_lost_lec.js')
                    if recalibrate_ptz:
                        print('Recalibrate Success')
                        start_tl = None
                    else:
                        print('Recalibrate Failure')

                else:
                    print('Waiting for Lecturer!')

            #Since we want to show something larger on the screen than the
            #original 320x240, we resize the image again
            #
            #Note that it would also be possible to keep the large version
            #of the base-image and make the result image a copy of this large
            #base image and use the scaling factor to draw the rectangle
            #at the right coordinates.
            largeResult = cv2.resize(resultImage,
                                     (OUTPUT_SIZE_WIDTH,OUTPUT_SIZE_HEIGHT))

            #Finally, we want to show the images on the screen
            cv2.imshow("base-image", baseImage)
            cv2.imshow("result-image", largeResult)

    #To ensure we can also deal with the user pressing Ctrl-C in the console
    #we have to check for the KeyboardInterrupt exception and destroy
    #all opencv windows and exit the application
    except KeyboardInterrupt as e:
        #turn_recal_ptz = execute_js('onvif_movement/recalibrate.js')
        cv2.destroyAllWindows()
        exit(0)


if __name__ == '__main__':
    detectAndTrackLargestFace()