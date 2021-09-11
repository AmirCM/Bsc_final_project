#!/usr/bin/env

import rospy
from std_msgs.msg import String


def talk_to_me():
    pub = rospy.Publisher("sampleTopic", String,queue_size=10)
    rospy.init_node('publisher', anonymous=True)
    rate = rospy.Rate(1)
    rospy.loginfo("Publisher sample node started!!!")

    while not rospy.is_shutdown():
        msg = "Hello ROS - %s" % rospy.get_time()
        print(msg)
        pub.publish(msg)
        rate.sleep()


    pass


print("THIS IS ROS TEST!!!!\n")
if __name__ == '__main__':
    try:
        talk_to_me()
    except rospy.ROSInterruptException:
        pass