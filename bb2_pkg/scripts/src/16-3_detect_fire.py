#!/usr/bin/env python
#-*- coding: utf-8 -*-

'''
불을 발견하고 이에 따라 비행을 제어하는 코드를 아래와 같다.
'''

import rospy, sys, cv2, os, datetime, time, threading, subprocess
from std_msgs.msg import String
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
from geometry_msgs.msg import Twist

class DetectFire:

  def __init__(self):
    self.sub = rospy.Subscriber("/image_raw", Image, self.callback)           # 스핑크스 구동할 떄 
    #self.sub = rospy.Subscriber("/bebop/image_raw", Image, self.callback)    # 실제 비밥 구동할 때
    self.bridge = CvBridge()
    self.cv_msg = cv2.imread("cimg.png")

  def callback(self,data):
    try:
      self.cv_msg = self.bridge.imgmsg_to_cv2(data, "bgr8")
        
    except CvBridgeError as e:
      print(e)

  def save_picture(self, picture):   #자동 켑쳐된 이미지 경로 및 저장 형식
    try:
      img = picture
      now = datetime.datetime.now()
      date = now.strftime('%Y%m%d')
      hour = now.strftime('%H%M%S')
      user_id = '00001'
      filename = '/home/kicker/fire_img/fire_{}_{}_{}.png'.format(date, hour, user_id)
      cv2.imwrite(filename, img)
    except CvBridgeError as e:
      print(e)

if __name__ == '__main__':

    rospy.init_node('fire_detector', anonymous=False)
    fly = rospy.Publisher('/bebop/cmd_vel', Twist, queue_size = 1)
    df = DetectFire()
    tw = Twist()
    rospy.sleep(1.0)
    i = 0
    
    #불을 인지했는지 판단하는 내부 변수를 설정한다.
    per_fire = 0
    #불을 인지하지 못한 시간을 저장하는 변수.
    ztime = 0.0
    #불을 인지했을 때의 시간을 저장하는 변수
    ftime = 0.0

    try:
        fire_cascade = cv2.CascadeClassifier('/home/kicker/catkin_ws/src/bb2_pkg/scripts/fire_detection.xml') # 훈련데이터를 읽어 온다

        while True:
           cod1 = rospy.get_param("/fire_detectorl/param_of_detector") #런치 파일의 16~17행
           if cod1 == "1":
            frame = df.cv_msg
            gray  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            fire  = fire_cascade.detectMultiScale(frame, 1.2, 5)

            #이는 불을 잠깐 인지했으나, 화면의 중앙에 맞추는 가운데 그 개체가 사라진 경우를 처리할 때 사용한다. 만일, 최초로 불을 발견한 시점과 불을 인지하지 못한 시점이 어느 한계를 넘어간다면 다시 Flytarget을 실행한다.
            
            if len(fire) == 0:
              #불이 발견되지 않은 경우에 "/play_alarm/fire_detection_state"를 0으로 설정한다. /play_alarm/fire_detection_state는 화재가 발생했음을 소리나 SMS 등으로 알리는 코드를 실행하기 위한 파라미터(parameter)이다.
              rospy.set_param("/play_alarml/fire_detection_state", False)
              #이전에 불을 발견했으나(즉, per_fire가 1이나) 발견되지 않은 시간을 저장한다
              if per_fire == 1:
                #불이 발견되지 않은 시간을 저장한다.
                ztime = time.time()
                #불을 발견했던 시간과 그 이후에 발견하지 못한 시간의 차이를 저장하기 위한 변수를 만든다.
                gap_time = ztime - ftime
                #불을 발견했던 시간과 그 이후에 발견하지 못한 시간의 차이가 30초 이상이면(즉 그 30초 동안 불을 발견하지 못했다면) 아래의 코드를 실행한다.
                if gap_time >= 15.0:
                  #불 감지 모드는 끝다.
                  per_fire = 0
                  #불을 발견했던 시간과 그 이후에 발견하지 못한 시간의 차이가 60초 이상이면(즉 그 60초 동안 불을 발견하지 못했다면) 다시 순행 비행을 시작한다.
                  #이후에 다시 실행하는 detect_fire.py에서 다시 FlyTarget.py를 시작할 수 있도록 i값을 다시 설정한다.
                  i = 0
                  #열려진 창을 닫는다.
                  cv2.destroyWindow('frame')
                  #다시 순행비행을 시작한다. 이를 위하여 Manager 노드의 파라미터 값을 변경시킨다.
                  rospy.set_param("/Fire_drone_managerl/order", 1)
                  #불 인식 코드를 비활성화한다.
                  rospy.set_param("/fire_detectorl/param_of_detector", "0")

            else:
              for (x,y,w,h) in fire:
                  cv2.rectangle(frame,(x-20,y-20),(x+w+20,y+h+20),(255,0,0),2)
                  roi_gray = gray[y:y+h, x:x+w]
                  roi_color = frame[y:y+h, x:x+w]

                  #일단 불을 발견했다면, 불을 인지했는지 판단하는 내부 변수(per_fire)를 변화시킨다.
                  per_fire = 1

                  #불을 발견했다면, 불을 인지한 시간을 저장한다.
                  ftime = time.time()

                  #불을 발견했다면 패트롤 모드(patrol mode)를 종료하고 adjust mode를 실행한다. 단, 한 번만 실행한다. 
                  if i == 0:
                    os.system("rosnode kill /fly_to_targetl")
                    i = 1

                  fx = x + (w * 0.5)
                  fy = y + (h * 0.5)

                  if ((fx >= 190)and(fx <= 450)) and ((fy >= 150)and(fy <= 330)):
                    #인식된 불이 화면의 중앙에 있을 경우에는 아래의 코드를 실행한다.
                    #드론의 비행을 멈춘다.
                    tw.linear.x = 0
                    tw.linear.y = 0
                    fly.publish(tw)
                    print("fire is center({}, {})".format(fx, fy))
                    #화재 경보를 알리는 코드를 활성화한다.
                    rospy.set_param("/play_alarml/fire_detection_state", True)
                    df.save_picture(frame)

                    #잠시 대기해 있다가 화재 경보를 알리는 코드를 비활성화한다.
                    rospy.set_param("/play_alarml/fire_detection_state", 0)

                    #처음 지점으로 되돌아 오는 비행 코드를 활성화한다.
                    rospy.set_param("/FlyBackl/param_of_back", "1")

                    #열려진 창을 닫는다.
                    cv2.destroyWindow('frame')
                    #불 인식 코드를 비활성화한다.
                    rospy.set_param("/fire_detectorl/param_of_detector", "0")
                    #코드를 종료한다.
                    exit()

                  elif ((fx >= 190) and (fx <= 450)) and ((fy >= 331) and(fy <= 480)):
                      #불이 화면의 아래에서 발견된 경우 뒤로 이동시킨다.
                      tw.linear.x = -0.2
                      tw.linear.y = 0
                      fly.publish(tw)
                      
                  elif ((fx >= 190) and (fx <= 450)) and ((fy >= 0 ) and(fy <= 149)):
                      #불이 화면의 위에서 발견된 경우 드론을 앞으로 이동시킨다.
                      tw.linear.x = 0.2
                      tw.linear.y = 0
                      fly.publish(tw)

                  elif ((fx >= 0) and (fx <= 189)) and ((fy >= 151 ) and(fy <= 329)):
                      #불이 화면의 왼쪽에서 발견된 경우 드론을 왼쪽으로 이동시킨다
                      tw.linear.x = 0
                      tw.linear.y = 0.2
                      fly.publish(tw)

                  elif ((fx >= 0) and (fx <=189)) and ((fy >= 331) and (fy <= 480)):
                      #불이 화면의 왼쪽 아래에서 발견된 경우 드론을 왼쪽 아래로 이동시킨다.
                      tw.linear.x = -0.2
                      tw.linear.y = 0.2
                      fly.publish(tw)

                  elif ((fx >= 0) and (fx <=189)) and ((fy >= 0) and (fy <= 149)):
                      #불이 화면의 왼쪽 위에서 발견된 경우 드론을 왼쪽 위로 이동시킨다.
                      #print("fire left up")
                      tw.linear.x = 0.2
                      tw.linear.y = 0.2
                      fly.publish(tw)

                  elif ((fx >= 450) and (fx <=640)) and ((fy >= 331) and (fy <= 640)):
                      #드론이 오른쪽 아래에서 발견된 경우 드론을 오른쪽 아래로 이동시킨다.
                      tw.linear.x = -0.2
                      tw.linear.y = -0.2
                      fly.publish(tw)

                  elif ((fx >= 450) and (fx <=640)) and ((fy >= 0) and (fy <= 149)):
                      #드론이 오른쪽 위에서 발견된 경우, 드론을 오른쪽 위로 이동시킨다.
                      tw.linear.x = 0.2
                      tw.linear.y = -0.2
                      fly.publish(tw)
                  elif ((fx >= 451) and (fx <= 640)) and ((fy >= 150 ) and(fy <= 330)):
                      #드론이 오른쪽에 있을 경우, 드론을 오른쪽으로 이동시킨다.
                      tw.linear.x = 0
                      tw.linear.y = -0.2
                      fly.publish(tw)
                  else:
                    pass

            cv2.imshow('frame', frame) #이미지를 띄운다.
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        rospy.spin()

    except KeyboardInterrupt:
        print("Shutting down")
