#pragma once

#include "esphome.h"
#include "lvgl.h"

namespace esphome {
namespace gui {

class GuiObject {
 protected:
  int x_ = 0;
  int y_ = 0;
  int w_ = 0;
  int h_ = 0;
  lv_style_t style;
  lv_obj_t* obj{nullptr};
  std::string text_{""};

  void setup();

 public:
  void update();
  void set_coords(int x, int y);
  void set_dimensions(int w, int h);
  void set_text(const char* val) { this->text_ = val; }
  inline const char* get_text() { return this->text_.c_str(); }
};

class GuiLabel : public GuiObject, public Component {
 protected:
 public:
  void update();
  void setup() override;
  void loop() override;
  void dump_config() override;
  float get_setup_priority() const override {
    return setup_priority::AFTER_BLUETOOTH;
  }

  void print(const char* text);
  void print(int x, int y, const char* text);
#ifdef USE_TIMEX
  void strftime(const char* format, time::ESPTime time);
  void strftime(int x, int y, const char* format, time::ESPTime time);
#endif
};

#ifdef USE_CHECKBOX
class GuiCheckbox : public GuiObject, public Component {
 protected:
  switch_::Switch* switch_;

 public:
  void setup() override;
  void loop() override;
  void dump_config() override;
  float get_setup_priority() const override {
    return setup_priority::AFTER_BLUETOOTH;
  }

  void set_switch(switch_::Switch* sw) { this->switch_ = sw; }
  static void event_callback(lv_event_t* event);
};
#endif

}  // namespace gui
}  // namespace esphome