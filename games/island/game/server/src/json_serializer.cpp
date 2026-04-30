/*
json_serializer.cpp - JSON serialization implementation

Author: Minju Seo
Date: 2026-01-24
*/

#include "json_serializer.h"

// 1. Serialize: Player -> JSON String
std::string JSONSerializer::serialize(const Player& player) {
    std::ostringstream oss;
    
    // JSON 규격에 맞춰 중괄호와 큰따옴표(\")를 정확히 배치합니다.
    oss << "{"
        << "\"id\":" << player.get_id() << ","
        << "\"name\":\"" << player.get_name() << "\","
        << "\"x\":" << player.get_x() << ","
        << "\"y\":" << player.get_y() << ","
        << "\"socket\":" << player.get_socket()
        << "}";
        
    return oss.str();
}

// 2. Deserialize: JSON String -> Player
Player JSONSerializer::deserialize(const std::string& data) {
    // 헬퍼 함수를 호출하여 각 필드 값을 추출합니다.
    int id = extractInt(data, "id");
    std::string name = extractString(data, "name");
    float x = extractFloat(data, "x");
    float y = extractFloat(data, "y");
    int socket = extractInt(data, "socket");

    return Player(id, name, x, y, socket);
}

std::string JSONSerializer::getName() const {
    return "JSON";
}

// --- Helper Functions ---

int JSONSerializer::extractInt(const std::string& json, const std::string& key) {
    std::string searchKey = "\"" + key + "\":";
    size_t start = json.find(searchKey) + searchKey.length();
    size_t end = json.find_first_of(",}", start);
    return std::stoi(json.substr(start, end - start));
}

float JSONSerializer::extractFloat(const std::string& json, const std::string& key) {
    std::string searchKey = "\"" + key + "\":";
    size_t start = json.find(searchKey) + searchKey.length();
    size_t end = json.find_first_of(",}", start);
    return std::stof(json.substr(start, end - start));
}

std::string JSONSerializer::extractString(const std::string& json, const std::string& key) {
    // 문자열 값은 "key":"value" 형태이므로 따옴표를 고려해야 합니다.
    std::string searchKey = "\"" + key + "\":\"";
    size_t start = json.find(searchKey) + searchKey.length();
    size_t end = json.find("\"", start);
    return json.substr(start, end - start);
}