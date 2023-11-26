#pragma once

#include "esphome.h"
#include "lvgl.h"

#ifdef USE_METER
// #include "esphome/components/sensor/sensor.h"
// using namespace sensor;
#endif

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

  lv_obj_t* setup();

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
#ifdef USE_TIME
  void strftime(const char* format, ESPTime time);
  void strftime(int x, int y, const char* format, ESPTime time);
#endif
};

#ifdef USE_CHECKBOX
class GuiCheckbox : public GuiObject, public Component {
 protected:
  switch_::Switch* switch_;
  bool switch_state;

 public:
  void setup() override;
  void loop() override;
  void dump_config() override;
  float get_setup_priority() const override {
    return setup_priority::AFTER_BLUETOOTH;
  }

  void set_switch(switch_::Switch* sw) { this->switch_ = sw; }
  // Callback for events generated from the UI (e.g., someone clicked the UI,
  // and now need to update switch value)
  static void gui_event_callback(lv_event_t* event);
  // Callback for events generated from the switch (e.g., someone changed switch
  // via Home Assistant and now need to update GUI)
  static void switch_event_callback(bool state);
};
#endif

#ifdef USE_ARC
#endif

#ifdef USE_BAR
#endif

#ifdef USE_BUTTON
#endif

#ifdef USE_BUTTON_MATRIX
#endif

#ifdef USE_DROPDOWN
#endif

#ifdef USE_IMAGE
#endif

#ifdef USE_ROLLER
#endif

#ifdef USE_SLIDER
#endif

#ifdef USE_SWITCH
#endif

#ifdef USE_TABLE
#endif

#ifdef USE_TEXTAREA
#endif

#ifdef USE_ANIMIMG
#endif

#ifdef USE_CALENDAR
#endif

#ifdef USE_CHART
#endif

#ifdef USE_COLORWHEEL
#endif

#ifdef USE_IMGBTN
#endif

#ifdef USE_KEYBOARD
#endif

#ifdef USE_LED
#endif

#ifdef USE_LIST
#endif

#ifdef USE_MENU
#endif

#ifdef USE_METER
class GuiMeter : public GuiObject, public Component {
 protected:
  // std::vector<esphome::sensor::Sensor *> sensors_;
  
 public:
  void setup() override;
  void loop() override;
  void dump_config() override;
  float get_setup_priority() const override {
    return setup_priority::AFTER_BLUETOOTH;
  }
};
#endif

#ifdef USE_MSGBOX
#endif

#ifdef USE_SPAN
#endif

#ifdef USE_SPINBOX
#endif

#ifdef USE_SPINNER
#endif

#ifdef USE_TABVIEW
#endif

#ifdef USE_TILEVIEW
#endif

#ifdef USE_WIN
#endif

#ifdef USE_FLEX
#endif

#ifdef USE_GRID
#endif

}  // namespace gui
}  // namespace esphome