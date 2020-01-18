#include <string>
#include <iostream>
#include <math.h>

#include "ros/ros.h"
#include "std_msgs/String.h"
#include "geometry_msgs/Point.h"

#include <boost/asio.hpp>                  //包含boost库函数
#include <boost/bind.hpp>


using namespace std;
using namespace boost::asio;
unsigned char buf1[10];
io_service iosev;
serial_port sp(iosev, "/dev/ttyUSB0");
 

int main(int argc, char *argv[]) {
    sp.set_option(serial_port::baud_rate(9600));
    sp.set_option(serial_port::flow_control());
    sp.set_option(serial_port::parity());
    sp.set_option(serial_port::stop_bits());
    sp.set_option(serial_port::character_size(8));
    ros::init(argc, argv, "stm2nuc_serial");

    ros::NodeHandle n;
    ros::Publisher point_pub = n.advertise<geometry_msgs::Point>("/WTR/serial/stm32", 1000);

    while (ros::ok()) {
        geometry_msgs::Point point;
        read(sp, buffer(buf1));
        for (int i = 0; i < 5; i++) {
            if (buf1[i] == 'w' && buf1[i + 1] == 't') {
                cout << "I'm in!!" << endl;

                switch(buf1[i+2])
                {
                    case 0: 
                        point.x = 0;
                        point.y = 0;
                        point.z = 1.5;
                        break;
                    case 1:
                        point.x = 0;
                        point.y = 3;
                        point.z = 1.5;
                        break;
                    case 2:
                        point.x = 1.5;
                        point.y = 3;
                        point.z = 1.5;
                        break;
                    default:
                        point.x = 0;
                        point.y = 0;
                        point.z = 1.5;

                }
                // point.x = buf1[i + 2];
                // point.y = buf1[i + 3];
                // point.z = buf1[i + 4];
                point_pub.publish(point);
                cout<<point<<endl;
                break;
            }
        }
        

        ros::spinOnce();
    }
    return 0;
}
