/*
binary_serializer.cpp - Binary serialization implementation
Author: Minju Seo
Date: 2026-01-24
*/

#include "binary_serializer.h"

// --- [공지] Base64 함수들은 반드시 serialize/deserialize 보다 위에 있어야 합니다! ---
static const char base64_chars[] = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";

// 제공된 Base64 encode 함수
std::string base64_encode(const unsigned char* data, size_t len) {
    std::string ret;
    int i = 0;
    unsigned char char_array_3[3];
    unsigned char char_array_4[4];
    while (len--) {
        char_array_3[i++] = *(data++);
        if (i == 3) {
            char_array_4[0] = (char_array_3[0] & 0xfc) >> 2;
            char_array_4[1] = ((char_array_3[0] & 0x03) << 4) + ((char_array_3[1] & 0xf0) >> 4);
            char_array_4[2] = ((char_array_3[1] & 0x0f) << 2) + ((char_array_3[2] & 0xc0) >> 6);
            char_array_4[3] = char_array_3[2] & 0x3f;
            for(i = 0; i < 4; i++) ret += base64_chars[char_array_4[i]];
            i = 0;
        }
    }
    if (i) {
        for(int j = i; j < 3; j++) char_array_3[j] = '\0';
        char_array_4[0] = (char_array_3[0] & 0xfc) >> 2;
        char_array_4[1] = ((char_array_3[0] & 0x03) << 4) + ((char_array_3[1] & 0xf0) >> 4);
        char_array_4[2] = ((char_array_3[1] & 0x0f) << 2) + ((char_array_3[2] & 0xc0) >> 6);
        for (int j = 0; j < i + 1; j++) ret += base64_chars[char_array_4[j]];
        while(i++ < 3) ret += '=';
    }
    return ret;
}

// 제공된 Base64 decode 함수
std::string base64_decode(const std::string& encoded_string) {
    size_t in_len = encoded_string.size();
    int i = 0, in_ = 0;
    unsigned char char_array_4[4], char_array_3[3];
    std::string ret;
    while (in_len-- && (encoded_string[in_] != '=')) {
        if (!isalnum(encoded_string[in_]) && encoded_string[in_] != '+' && encoded_string[in_] != '/') {
            in_++; continue;
        }
        char_array_4[i++] = encoded_string[in_++];
        if (i == 4) {
            for (i = 0; i < 4; i++) char_array_4[i] = strchr(base64_chars, char_array_4[i]) - base64_chars;
            char_array_3[0] = (char_array_4[0] << 2) + ((char_array_4[1] & 0x30) >> 4);
            char_array_3[1] = ((char_array_4[1] & 0xf) << 4) + ((char_array_4[2] & 0x3c) >> 2);
            char_array_3[2] = ((char_array_4[2] & 0x3) << 6) + char_array_4[3];
            for (i = 0; i < 3; i++) ret += char_array_3[i];
            i = 0;
        }
    }
    if (i) {
        for (int j = i; j < 4; j++) char_array_4[j] = 0;
        for (int j = 0; j < 4; j++) char_array_4[j] = strchr(base64_chars, char_array_4[j]) - base64_chars;
        char_array_3[0] = (char_array_4[0] << 2) + ((char_array_4[1] & 0x30) >> 4);
        char_array_3[1] = ((char_array_4[1] & 0xf) << 4) + ((char_array_4[2] & 0x3c) >> 2);
        for (int j = 0; j < i - 1; j++) ret += char_array_3[j];
    }
    return ret;
}

// --- 실제 구현부 ---

std::string BinarySerializer::serialize(const Player& player) {
    PlayerData data;
    std::memset(&data, 0, sizeof(PlayerData)); // 패딩 0으로 초기화

    data.id = player.get_id(); // 수치 데이터 복사
    data.x = player.get_x();
    data.y = player.get_y();
    data.socket = player.get_socket();

    std::strncpy(data.name, player.get_name().c_str(), 31); // 최대 31자 복사
    data.name[31] = '\0'; // 널 종료 보장

    // reinterpret_cast를 사용하여 구조체를 바이트 스트림으로 변환
    return base64_encode(reinterpret_cast<const unsigned char*>(&data), sizeof(PlayerData));
}

Player BinarySerializer::deserialize(const std::string& data) {
    std::string decoded = base64_decode(data); // Base64 디코딩
    
    if (decoded.size() < sizeof(PlayerData)) { // 크기 검증
        return Player();
    }

    // 바이트 데이터를 다시 구조체로 해석
    const PlayerData* pData = reinterpret_cast<const PlayerData*>(decoded.data());
    return Player(pData->id, std::string(pData->name), pData->x, pData->y, pData->socket);
}

std::string BinarySerializer::getName() const {
    return "Binary";
}