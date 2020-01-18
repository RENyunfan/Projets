//
// Created by ou on 2019/12/15.
//

#include "ros/ros.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include "geometry_msgs/Pose.h"
#include "std_msgs/String.h"
#include "iostream"
#include "std_msgs/Char.h"
using namespace std;


/*
 *
 * R(Ready)
 * |
 * |
 * |      1 2
 * |     3 4 5
 * |      6 7
 * |____________________________
 *
 * H
 * |       1     2
 * |       3  4  5
 * |       6     7
 * |
 * |___________________________________
 * I
 * |          1       2
 * | 3        4       5
 * | 6        7
 * |
 * |___________________________________
 * T
 * |       3  1  2
 * |          4       5
 * | 6        7
 * |
 * |___________________________________
 *
 *
 *    GRID 栅格
 *    OFFSET 偏值
 *
 *
 * */
#define GRID 1.00
#define OFFSET 4.00
const int H = 0,I=1,T=2;
float XmapH[] = {0,2,0,1,2,0,2};
float YmapH[] = {2,2,1,1,1,0,0};
float XmapI[] = {1,5,-2,1,5,-2,1};
float YmapI[] = {2,2,1,1,1,0,0};
float XmapT[] = {1,2,0,1,5,-2,1};
float YmapT[] = {2,2,2,1,1,0,0};
char Mode='R';
geometry_msgs::Pose send_pose;
void setPose(int ID,char C){
    switch (C){
        case 'H':
        {
            send_pose.position.x = XmapH[ID] * GRID + OFFSET;
            send_pose.position.y = YmapH[ID] * GRID + OFFSET;
            send_pose.position.z = ID;
            break;
        }
        case 'I':
        {
            send_pose.position.x = XmapI[ID] * GRID + OFFSET;
            send_pose.position.y = YmapI[ID] * GRID + OFFSET;
            send_pose.position.z = ID;
            break;
        }
        case 'T':
        {
            send_pose.position.x = XmapT[ID] * GRID + OFFSET;
            send_pose.position.y = YmapT[ID] * GRID + OFFSET;
            send_pose.position.z = ID;
            break;
        }
        default:
            send_pose.position.z = 99;
    }
}

void modeCallback(const std_msgs::Char::ConstPtr& msg){
    Mode = msg->data;
}

int main (int argc, char** argv)
{
    ros::init(argc, argv, "formate_master");
    ros::NodeHandle nh;
    ros::Publisher server_pub = nh.advertise<geometry_msgs::Pose>("/master_topic", 1000);
    ros::Subscriber subCom  = nh.subscribe("/WTR/mode",1000,modeCallback);
    ros::Rate loop_rate(10);
    while(ros::ok()) {
        for(int id=0;id<3;id++){
            setPose(id,Mode);
            server_pub.publish(send_pose);
            loop_rate.sleep();
        }
        cout<<Mode<<endl;


        ros::spinOnce();

    }
    return 0;
}
