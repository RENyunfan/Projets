#pragma once
#ifndef wtr_para_h
#define wtr_para_h

#include "geometry_msgs/Twist.h"
#include "geometry_msgs/Point.h"

struct PID_t{
    float Kp,Ki,Kd;
    float cur_error;
    float ref;
    float output;
    float outputMax = 6;
    float error[2];
};
enum WTR_function_state{
    WTR_faild,
    WTR_success
};

enum workstate_e{
    GROUND,
    LAND,
    P2P_FLYING,
    SEARCH,
    CATCH,
    TAKEOFF,
    STAY
};
struct UAV_t{
    geometry_msgs::Twist WTR_twist;
    geometry_msgs::Point Target_pose,Present_pose;
    workstate_e Workstate;
    PID_t Position[3];
};

const int NOW = 0;
const int LAST = 1;
const int X = 0;
const int Y = 1;
const int Z = 2;

void PID_Calc(PID_t *pid);

#endif
