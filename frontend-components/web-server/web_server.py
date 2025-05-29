import flask as fsk
import os
import cv2
import numpy as np
import multiprocessing as mpc
import time
import socket
import datetime

def main(ip_2_connect = "192.168.1.188"):

    os.chdir("/home/debian/SmartHome/web-server/")

    app = fsk.Flask("SmartHome", root_path="/home/debian/SmartHome/web-server/")
    app.secret_key = "nxp12345"

    '''
    
    connect to processing server
    
    '''

    sock = socket.socket()
    ok = False

    while ok is False:
        try:
            sock.connect((ip_2_connect, 8080))
            ok = True
        except:
            print("Connection refused, trying again...")
            time.sleep(1)
            
    def sendCommand(command):
        sock.send(command.encode())
        now = datetime.datetime.now()
        print("\033[34m  WEB =>\033[0mlog: {}:{}:{} | {}".format(now.hour, now.min, now.second, command))
    
    sendCommand("Hello I am WEB!!")
    var = sock.recv(2048).decode()

    devices = {}

    for entry in var.split("\n\n"):
        type, device_names = entry.split(":\n")
        _, location, type, _ = type.split('/')
        device_names = device_names.split('\n')

        if not type in devices.keys(): 
            devices[type] = {}

        devices[type][location] = device_names


    @app.route('/')
    def init():
        return fsk.redirect(fsk.url_for("livingroom"))
    
    '''
    Rooms loading functions
    & display
    '''

    @app.route('/livingroom')
    def livingroom():
        return fsk.render_template("livingroom.html", bulbs_list = devices["Lights"]["Livingroom"])
    

    @app.route('/bedroom1')
    def bedroom1():
        return fsk.render_template("bedroom1.html")
    

    @app.route('/bedroom2')
    def bedroom2():
        return fsk.render_template("bedroom2.html")
    

    @app.route('/bathroom')
    def bathroom():
        return fsk.render_template("bathroom.html")
    

    @app.route('/kitchen')
    def kitchen():
        return fsk.render_template("kitchen.html")
    

    @app.route('/garage')
    def garage():
        return fsk.render_template("garage.html")

    '''
    Bulbs functions
    '''

    @app.route('/bulb_select', methods=["POST"])
    def bulb_select():
        bulb = fsk.request.json.get("value", 0)

        return fsk.jsonify({"message":"Bulb selected"})


    @app.route('/bulb_bttn_set', methods=["POST", "GET"])
    def bulb_bttn_set():
        state = fsk.request.json.get("value", 0)
        bulb  = fsk.request.json.get("bulb", 0)
        room  = fsk.request.json.get("room", 0)
        sendCommand("BULB:{}:{}:{}".format(room, bulb, state))

        return fsk.jsonify({"message":"Bulb color changed"})

    '''
    Camera functions
    '''

    def gen_frames(room):  
        
        frame_dict = {
            "Bedroom1"   : '',
            "Livingroom" : ''
        }

        pipeline = 'imxcompositor_g2d name=comp sink_0::xpos=0 sink_0::ypos=0 sink_1::xpos=0 sink_1::ypos=720 ' \
                    '! queue ! appsink sync=false rtspsrc location="rtsp://Tapo-Cam-1:nxp12345@192.168.1.201/stream2" ! rtph264depay ! h264parse ! queue ! v4l2h264dec ' \
                    '! queue ! comp. rtspsrc location="rtsp://Tapo-Cam-2:nxp12345@192.168.1.202/stream2" ! rtph264depay ! h264parse ! queue ! v4l2h264dec ! queue ! comp. '
        

        cam = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)

        while True:
            ok, frame = cam.read()
            if ok:
                for i, k in enumerate(frame_dict.keys()):
                    frame_dict[k] = frame[i * 720 : (i + 1) * 720, :, :]

                if room in frame_dict.keys():
                    ret, buffer = cv2.imencode('.jpg', frame_dict[room])
                    frame = buffer.tobytes()
            else:
                frame = np.random.randint(255, size=(16,9,3),dtype=np.uint8)
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    @app.route('/video_feed_livingroom')
    def video_feed_livingroom():
        return fsk.Response(gen_frames("Livingroom"), mimetype='multipart/x-mixed-replace; boundary=frame')
    
    @app.route('/video_feed_bedroom_1')
    def video_feed_bedroom_1():
        return fsk.Response(gen_frames("Bedroom1"), mimetype='multipart/x-mixed-replace; boundary=frame')

    @app.route('/camera_move', methods=["POST", "GET"])
    def camera_move():
        room      = fsk.request.json.get("room", 0)
        direction = fsk.request.json.get("direction", 0)
        sendCommand("CAMERA:{}:{}".format(room, direction))

        return fsk.jsonify({"message":"Camera moved"})

    app.logger.disabled = True
    app.run(debug=False, host="0.0.0.0", port=5000)

if __name__ == "__main__":
    main()