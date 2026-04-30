/*
text_serializer.cpp - Text serialization implementation

Author: Minju Seo
Date: 2026-01-24
*/

#include "text_serializer.h"

// 1. Serialize: Player -> "id|name|x|y|socket"
std::string TextSerializer::serialize(const Player& player) {
    std::ostringstream oss;
    
    // 파이프(|)를 구분자로 사용하여 각 필드를 결합합니다.
    // ostringstream이 숫자 타입을 자동으로 문자열로 변환해줍니다.
    oss << player.get_id() << "|"
        << player.get_name() << "|"
        << player.get_x() << "|"
        << player.get_y() << "|"
        << player.get_socket();
        
    return oss.str();
}

// 2. Deserialize: "id|name|x|y|socket" -> Player
Player TextSerializer::deserialize(const std::string& data) {
    std::istringstream iss(data);
    std::string field;
    
    // getline과 '|'를 사용하여 데이터를 하나씩 추출합니다.
    std::getline(iss, field, '|');
    int id = std::stoi(field);  // 정수 변환
    
    std::getline(iss, field, '|');
    std::string name = field;
    
    std::getline(iss, field, '|');
    float x = std::stof(field); // 실수 변환
    
    std::getline(iss, field, '|');
    float y = std::stof(field);
    
    std::getline(iss, field, '|');
    int socket = std::stoi(field);

    // 추출한 데이터로 새로운 Player 객체를 생성해 반환합니다.
    return Player(id, name, x, y, socket);
}

std::string TextSerializer::getName() const {
    return "Text";
}