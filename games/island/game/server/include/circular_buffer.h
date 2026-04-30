/*
circular_buffer.h - Circular buffer (ring buffer) template class

A fixed-size buffer that wraps around when full.
Used as the base for position smoothing strategies.

Author: Minju Seo
Date: 2026-02-23
Project: Project 2 - Network Position Buffering
*/

#ifndef CIRCULAR_BUFFER_H
#define CIRCULAR_BUFFER_H

#include <stdexcept>

template<typename T>
class CircularBuffer {
protected:
    T* buffer;           // Array to store elements
    int capacity;        // Maximum number of elements
    int head;            // Index for next dequeue (oldest)
    int tail;            // Index for next enqueue (newest)
    int count;           // Current number of elements
    
public:
    /**
     * Constructor - creates empty circular buffer
     * * @param cap Maximum capacity of the buffer
     */
    CircularBuffer(int cap) : capacity(cap), head(0), tail(0), count(0) {
        if (cap <= 0) throw std::invalid_argument("Capacity must be positive");
        buffer = new T[capacity];
    }
    
    /**
     * Destructor - clean up allocated memory
     */
    virtual ~CircularBuffer() {
        delete[] buffer;
    }
    
    /**
     * Add element to the buffer
     * * @param item Element to add
     * @return true if successful, false if buffer is full
     */
    bool enqueue(const T& item) {
        if (is_full()) {
            return false;
        }
        
        buffer[tail] = item;
       // calculate next tail position
        tail = (tail + 1) % capacity;
        count++;
        return true;
    }
    
    /**
     * Remove and return element from buffer
     * * @return The oldest element in the buffer
     * @throws std::runtime_error if buffer is empty
     */
    T dequeue() {
        if (is_empty()) {
            throw std::runtime_error("Buffer is empty");
        }
        
        T item = buffer[head];
        // calculate next head position
        head = (head + 1) % capacity;
        count--;
        return item;
    }
    
    /**
     * Get element at logical index (0 = oldest, size()-1 = newest)
     * * @param index Logical index (0-based from head)
     * @return Element at that position
     * @throws std::out_of_range if index is invalid
     */
    T get(int index) const {
        if (index < 0 || index >= count) {
            throw std::out_of_range("Index out of bounds");
        }
        
        // Calculate actual index in the buffer array
        int actual_index = (head + index) % capacity;
        return buffer[actual_index];
    }
    
    /**
     * Look at the oldest element without removing it
     * * @return The oldest element
     * @throws std::runtime_error if buffer is empty
     */
    T peek() const {
        if (is_empty()) {
            throw std::runtime_error("Buffer is empty");
        }
        return buffer[head];
    }
    
    /**
     * Check if buffer is empty
     */
    bool is_empty() const {
        return count == 0;
    }
    
    /**
     * Check if buffer is full
     */
    bool is_full() const {
        return count == capacity;
    }
    
    /**
     * Get current number of elements
     */
    int size() const {
        return count;
    }
    
    /**
     * Get maximum capacity
     */
    int get_capacity() const {
        return capacity;
    }
    
    /**
     * Remove all elements from buffer
     */
    void clear() {
        head = 0;
        tail = 0;
        count = 0;
    }
};

#endif // CIRCULAR_BUFFER_H