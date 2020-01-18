#!/usr/bin/env python
#-*-coding=utf-8-*-
import rospy
from std_msgs.msg import String

def talker():
    pub = rospy.Publisher('mode', String, queue_size=10)
    rospy.init_node('modePub', anonymous=True)
    rate = rospy.Rate(50) # 10hz
    while not rospy.is_shutdown():
        try:
            mode = input("input mode:")
        except:
            continue
        hello_str = mode
        rospy.loginfo(hello_str)
        pub.publish(hello_str)
        rate.sleep()
 
if __name__ == '__main__':
    try:
        talker()
    except rospy.ROSInterruptException:
        pass
