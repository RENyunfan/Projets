#include <string>
#include <iostream>
#include <math.h>
#include "ros/ros.h"
#include "std_msgs/String.h"
#include "geometry_msgs/Point.h"
#include "geometry_msgs/Pose.h"
#include "geometry_msgs/Twist.h"
#include "move_base_msgs/MoveBaseActionGoal.h"
#include "eigen3/Eigen/Geometry"

const int ID = 0x00;
using namespace std;
geometry_msgs::Pose target_pose,fdb_pose;
geometry_msgs::Twist pub_vel;
#define Kp_x 0
#define Kp_y 0
#define Ki_x 0


void tarCallback(const geometry_msgs::Pose::ConstPtr& msg)
{
    target_pose= *msg;
}

void fdbCallback(const geometry_msgs::Pose::ConstPtr& msg)
{
    fdb_pose= *msg;
}

float dis(){
    float x2 = (target_pose.position.x-fdb_pose.position.x) * (target_pose.position.x-fdb_pose.position.x);
    float y2 = (target_pose.position.y-fdb_pose.position.y) * (target_pose.position.y-fdb_pose.position.y);
    return sqrt(x2+y2);
}
float positon_N[2];
void volcility_pid()
{

    Eigen::Quaterniond quaternion(fdb_pose.orientation.w,target_pose.orientation.x,target_pose.orientation.y,target_pose.orientation.z);
    Eigen::Vector3d eulerAngle=quaternion.matrix().eulerAngles(2,1,0);
    pub_vel.linear.x=(sqrt(target_pose.position.x-fdb_pose.position.x)+sqrt(target_pose.position.y-fdb_pose.position.y))*Kp_x;
    pub_vel.angular.z=(atan((sqrt(target_pose.position.x-fdb_pose.position.x))/(sqrt(target_pose.position.y-fdb_pose.position.y)))-eulerAngle.z())*Kp_y;
    if(pub_vel.linear.x>0.5)
    {
        pub_vel.linear.x=0.5;
    }

}
int main(int argc, char *argv[]) {
    ros::init(argc, argv, "formate_slave");
    ros::NodeHandle n;
    ros::Publisher   vel_pub = n.advertise<geometry_msgs::Twist>("/cmd_vel", 1000);
    ros::Subscriber  tar_sub = n.subscribe("/WTR/traget_pose", 1000, tarCallback);
    ros::Subscriber  fdb_sub = n.subscribe("/robot_pose", 1000, fdbCallback);

    while (ros::ok()) {


        volcility_pid();
        if(dis()<0.05){
            pub_vel.linear.x = 0;
            pub_vel.angular.z=0;
        }
        vel_pub.publish(pub_vel);
        ros::spinOnce();
    }

    return 0;
}

