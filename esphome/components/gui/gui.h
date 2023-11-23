#pragma once

#include "esphome.h"
#include "gui_objects.h"
#include "lvgl.h"

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
#if LV_USE_LOG
  static void lv_esp_log(const char *buf);
#endif

  void set_display(DisplayBuffer *display) { this->display_ = display; }
  static void refresh(lv_disp_drv_t *disp_drv, const lv_area_t *area,
                          lv_color_t *buf);

 protected:
  void refresh_internal_(lv_disp_drv_t *disp_drv, const lv_area_t *area,
                    lv_color_t *buf);

  DisplayBuffer *display_{nullptr};

  lv_disp_t *lv_disp_{nullptr};
  lv_disp_drv_t disp_drv_{};
  lv_disp_draw_buf_t draw_buf_{};
  lv_disp_rot_t get_lv_rotation();

 private:
  HighFrequencyLoopRequester high_freq_;
};

}  // namespace gui
}  // namespace esphome