/*
position.h - Position structure for network buffering

Simple 2D position with timestamp.

*/

#ifndef POSITION_H
#define POSITION_H

/**
 * Simple 2D position structure
 */
struct Position {
    float x;
    float y;
    long timestamp;  // When this position was recorded (milliseconds)
    
    Position() : x(0), y(0), timestamp(0) {}
    Position(float x_pos, float y_pos, long ts = 0) 
        : x(x_pos), y(y_pos), timestamp(ts) {}
};

#endif // POSITION_H