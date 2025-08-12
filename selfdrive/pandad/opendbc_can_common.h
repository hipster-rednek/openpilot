#pragma once
#include <cstdint>
#include <vector>

struct CanFrame {
  long src;
  uint32_t address;
  std::vector<uint8_t> dat;
};

struct CanData {
  uint64_t nanos;
  std::vector<CanFrame> frames;
};
