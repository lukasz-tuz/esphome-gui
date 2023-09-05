#pragma once

#include <cstdarg>
#include <vector>

#include "display.h"
#include "display_color_utils.h"

#include "esphome/core/component.h"
#include "esphome/core/defines.h"

namespace esphome {
namespace display {

class DisplayBuffer : public Display {
 public:
  /// Get the width of the image in pixels with rotation applied.
  int get_width() override;
  /// Get the height of the image in pixels with rotation applied.
  int get_height() override;

  /// Set a single pixel at the specified coordinates to the given color.
  void draw_pixel_at(int x, int y, Color color) override;

  virtual int get_height_internal() = 0;
  virtual int get_width_internal() = 0;

#ifdef USE_GUI
  // public DisplayBuffer methods for LVGL
  virtual void write_display_data() = 0;
  virtual void update() = 0;
  virtual size_t get_buffer_length_() = 0;
  uint8_t *get_buffer() { return this->buffer_; }
#endif

 protected:
  virtual void draw_absolute_pixel_internal(int x, int y, Color color) = 0;

  void init_internal_(uint32_t buffer_length);

  uint8_t *buffer_{nullptr};
};

}  // namespace display
}  // namespace esphome
