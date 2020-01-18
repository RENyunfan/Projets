#include <sstream>

#include "ros/ros.h"
#include "std_msgs/String.h"
#include "std_msgs/Int8.h"
#include "geometry_msgs/Twist.h"

#include <boost/asio.hpp>
#include <boost/bind.hpp>

using namespace std;
using namespace boost::asio;
//####################################
unsigned char buf[7]={'w','t','r',50,50,50,0x00};
io_service iosev;
serial_port sp(iosev, "/dev/ttyUSB0");

bool cmd_update=false; //保持同步
bool twist_update=false;

std_msgs::Int8 g_cmd;

void CmdCallback(const std_msgs::Int8::ConstPtr& _cmd);
void TwistCallback(const geometry_msgs::Twist::ConstPtr& _twist);
//####################################


int main(int argc, char *argv[])
{
    sp.set_option(serial_port::baud_rate(115200));  //波特率
    sp.set_option(serial_port::flow_control());		//流控制(none/software/hardware)
    sp.set_option(serial_port::parity());			//奇偶校验(none/odd/even)
    sp.set_option(serial_port::stop_bits());		//停止位(one/onepointfive/two)
    sp.set_option(serial_port::character_size(8));	//字符大小

    ros::init(argc, argv, "nuc2fc");

    ros::NodeHandle n;

    ros::Subscriber sub_cmd = n.subscribe("/WTR/Target/Commond", 1, CmdCallback);
    ros::Subscriber sub_twist = n.subscribe("/WTR/Target/Twist", 1, TwistCallback);
    while (ros::ok()) {
        ros::spinOnce();
    }
    return 0;
}


void CmdCallback(const std_msgs::Int8::ConstPtr& _cmd)
{
    cmd_update=true;
    g_cmd.data=_cmd->data;
    if(g_cmd.data ==4)
    {
                buf[6]=4;
    write(sp, buffer(buf,7));
    }


}
void TwistCallback(const geometry_msgs::Twist::ConstPtr& _twist)
{
    twist_update=true;
    if(g_cmd.data == 7)
    {    buf[3]=_twist->linear.x+50;
    cout<<*_twist<<endl;
    buf[4]=_twist->linear.y+50;
    buf[5]=50;//_twist->angular.z;
    buf[6]=g_cmd.data;
    for(int i=0;i<7;i++)
        cout<<buf[i]<<endl;
    cout<<"123"<<endl;
    write(sp, buffer(buf,7));}


} 
