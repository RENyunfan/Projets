//
// Created by chrisliu on 2019/9/4.
//
#include "ros/ros.h"
#include <nav_msgs/Path.h>
#include <nav_msgs/Odometry.h>
#include <geometry_msgs/PoseStamped.h>

ros::Publisher pub_path;
nav_msgs::Path path;

void point_callback(const nav_msgs::OdometryConstPtr &odom) {
    geometry_msgs::PoseStamped poseStamped;
    poseStamped.header = odom->header;
    poseStamped.pose = odom->pose.pose;
    path.poses.push_back(poseStamped);
    pub_path.publish(path);
}

int main(int argc, char **argv) {
    ros::init(argc, argv, "point2path");
    ros::NodeHandle n;

    ros::Subscriber sub_point = n.subscribe("/camera/odom/sample", 1, point_callback);
    pub_path = n.advertise<nav_msgs::Path>("/WTR/Path", 1);

    path.header.frame_id = "camera_odom_frame";

    while (ros::ok()) {
        ros::spinOnce();
    }

    return 0;
}
