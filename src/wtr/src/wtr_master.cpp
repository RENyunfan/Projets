#include "ros/ros.h"
#include "nav_msgs/Odometry.h"
#include "std_msgs/Int8.h"
#include "iostream"
#include "cmath"
#include "wtr_UAVpara.h"
#include "geometry_msgs/Twist.h"

using namespace std;
UAV_t UAV;
string rs_topic = "/camera/odom/sample";
string serial_topic = "/WTR/serial/stm32";
std_msgs::Int8 Commond;
ros::Publisher pub_com;
ros::Publisher pub_vol;
void UAV_init() {
    //初始化PID
    for (int i = 0; i < 3; i++) {
        UAV.Position[i].Kp = 0.1;
        UAV.Position[i].Ki = 0.05;
        UAV.Position[i].Kd = 0;
        UAV.Position[i].cur_error = 1;
        UAV.Position[i].outputMax = 15;
    }
    // 启动ROS节点

    UAV.Workstate = P2P_FLYING;

}

void rs_callBack(const nav_msgs::Odometry::ConstPtr &fb_odom) {
    //realsense's axis need to remap
    // y+ is left x+ is forward
    UAV.Present_pose.x = fb_odom->pose.pose.position.y * 100 * (-1.0) ;       //change y
    UAV.Present_pose.y = fb_odom->pose.pose.position.x * 100; //change x
    UAV.Present_pose.z = fb_odom->pose.pose.position.z * 100;

}

void serial_callBack(const geometry_msgs::Point::ConstPtr &fb_target) {

    UAV.Target_pose.x = fb_target->x * 100;
    UAV.Target_pose.y = fb_target->y * 100;
    UAV.Target_pose.z = fb_target->z * 100;
}

/*
Calculate Eular distance
*/
bool is_near() {
    float dis = pow((UAV.Present_pose.x-UAV.Target_pose.x),2) +
                pow((UAV.Present_pose.y-UAV.Target_pose.y),2) +
                pow((UAV.Present_pose.z-UAV.Target_pose.z),2);
    if(sqrt(dis) < 10)
                
                {
                    return true;
                }
    return false;
}


void Point_2_Point() {
    UAV.Position[X].cur_error = UAV.Target_pose.x - UAV.Present_pose.x;
    UAV.Position[Y].cur_error = UAV.Target_pose.y - UAV.Present_pose.y;
    UAV.Position[Z].cur_error = UAV.Target_pose.z - UAV.Present_pose.z;
    // cout<<"x:"<<UAV.Position[X].cur_error<<endl;
    // cout<<"y:"<<UAV.Position[Y].cur_error<<endl;
    // cout<<"z:"<<UAV.Position[Z].cur_error<<endl;

    PID_Calc(&UAV.Position[X]);
    UAV.WTR_twist.linear.x = UAV.Position[X].output;
    PID_Calc(&UAV.Position[Y]);
    UAV.WTR_twist.linear.y = UAV.Position[Y].output;
//    PID_Calc(Position[Z]);
//    UAV.WTR_twist.linear.z = UAV.Position[Z].output;

}

void PID_Calc(PID_t *pid) {

    pid->output = pid->Kp * (pid->cur_error) + pid->Ki * pid->cur_error +
                   pid->Kd * (pid->cur_error - 2 * pid->error[1] + pid->error[0]);
    ROS_INFO("error:%f output:%f",pid->cur_error,pid->output);
    pid->error[0] = pid->error[1];
    pid->error[1] = pid->cur_error;
    /* PID amplitude limitation */
    if (pid->output > pid->outputMax) pid->output = pid->outputMax;
    if (pid->output < -pid->outputMax) pid->output = -pid->outputMax;
}

int main(int argc, char **argv) {
    ros::init(argc, argv, "Master");
    ros::NodeHandle Master_n;
    UAV_init();
    // Begin ROS
    pub_com = Master_n.advertise<std_msgs::Int8>("/WTR/Target/Commond", 1);
    pub_vol = Master_n.advertise<geometry_msgs::Twist>("/WTR/Target/Twist", 1);
    ros::Subscriber RealSense = Master_n.subscribe("/camera/odom/sample", 1, rs_callBack);
    ros::Subscriber Serial = Master_n.subscribe("/WTR/serial/stm32", 1, serial_callBack);
    while (ros::ok()) {
        /* code for loop body */
//        if (UAV.Workstate)
	if (is_near()) UAV.Workstate = STAY;
    else UAV.Workstate = P2P_FLYING;
       switch (UAV.Workstate)
       {
           case GROUND:
               Commond.data = 0;
               break;
           case TAKEOFF:
               Commond.data = 7;
               break;
           case LAND:
               Commond.data = 9;
               break;
           case P2P_FLYING:
               Point_2_Point();
               pub_vol.publish(UAV.WTR_twist);
               Commond.data = 7;
//               cout<<UAV.WTR_twist<<endl;
               break;
           case STAY:
           Point_2_Point();
               pub_vol.publish(UAV.WTR_twist);
               Commond.data = 4;
               break;
           default:
               Commond.data = 4;
   }

   pub_com.publish(Commond);
    ros::spinOnce();
}
//End ROS
return 0;
}

