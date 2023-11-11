#pragma once

#include "esphome.h"
#include "lvgl.h"
#include "gui_objects.h"

namespace esphome {

// forward declare DisplayBuffer
namespace display {
class DisplayBuffer;
}  // namespace display

namespace gui {

using namespace display;

class GuiComponent : public Component {
 public:
  void setup() override;
  void loop() override;
  void dump_config() override;
  float get_setup_priority() const override {
    return setup_priority::PROCESSOR;
  }

  void set_display(DisplayBuffer *display) { this->display_ = display; }

 protected:
  DisplayBuffer *display_{nullptr};
  lv_disp_t *lv_disp_{nullptr};

  lv_disp_rot_t get_lv_rotation();

 private:
  HighFrequencyLoopRequester high_freq_;
};

}  // namespace gui
}  // namespace esphome