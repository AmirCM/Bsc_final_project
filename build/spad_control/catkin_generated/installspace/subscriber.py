#!/usr/bin/env

from re import T
import rospy
from rospy.core import loginfo
from std_msgs.msg import String

def listener_callback(data: String):
    rospy.loginfo("Received data: %s", data.data)

    pass

def listener():
    rospy.init_node('Subscriber_Node')
    rospy.Subscriber("sampleTopic", String, listener_callback)
    rospy.spin()
    pass


print("THIS IS Subscriber ROS TEST!!!!\n")
if __name__ == '__main__':
    try:
        listener()
    except rospy.ROSInterruptException:
        pass