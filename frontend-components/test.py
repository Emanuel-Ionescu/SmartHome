import cv2
import multiprocessing as mpc

def proc1():

    cam1 = cv2.VideoCapture(
        'gst-launch-1.0 imxcompositor_g2d name=comp sink_0::xpos=0 sink_0::ypos=0 sink_1::xpos=0 sink_1::ypos=720 ! queue ! appsink sync=false rtspsrc location="rtsp://Tapo-Cam-1:nxp12345@192.168.1.201/stream2" ! rtph264depay ! h264parse ! queue ! v4l2h264dec ! queue ! comp. rtspsrc location="rtsp://Tapo-Cam-2:nxp12345@192.168.1.202/stream2" ! rtph264depay ! h264parse ! queue ! v4l2h264dec ! queue ! comp. ',
        cv2.CAP_GSTREAMER
        )
    
    while True:
        _, frame = cam1.read()

        f1 = frame[:720, :, :]
        f2 = frame[720:, :, :]

        f1 = cv2.resize(f1, (300, 300))
        f2 = cv2.resize(f2, (300, 300))


        frame = cv2.hconcat([f1, f2])

        #cv2.imshow("test", frame)
        cv2.imshow("f1", f1)
        cv2.imshow("f2", f2)

        cv2.waitKey(1)
        print(frame.shape)

proc1()
