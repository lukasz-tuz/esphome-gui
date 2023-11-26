#include "gui_objects.h"
#include "lvgl.h"

namespace esphome {
namespace gui {

static const char *const TAG = "gui.object";

/// GUI Object

inline void GuiObject::update() {
  if (this->obj == nullptr) return;
  ESP_LOGV(TAG, "\tsetting object's position and size");
  ESP_LOGV(TAG, "\t\tcoordinates: (%i, %i)", this->x_, this->y_);
  ESP_LOGV(TAG, "\t\tdimensions: (%i, %i)", this->w_, this->h_);
  lv_obj_set_pos(this->obj, this->x_, this->y_);
  lv_obj_set_size(this->obj, this->w_, this->h_);
}
void GuiObject::set_coords(int x, int y) {
  this->x_ = x;
  this->y_ = y;
}
void GuiObject::set_dimensions(int w, int h) {
  this->w_ = w;
  this->h_ = h;
}
lv_obj_t *GuiObject::setup() {
  lv_style_init(&this->style);
  return lv_scr_act();
}

/// GUI Label

void GuiLabel::update() {
  if (this->obj == nullptr) return;
  GuiObject::update();
  lv_label_set_text(this->obj, this->text_.c_str());
  ESP_LOGV(TAG, "\tCalling lv_label_set_text");
}
void GuiLabel::setup() {
  lv_obj_t *screen = GuiObject::setup();

  if (screen == nullptr) {
    // Exit with a warning. Due to different timings etc., it may happen that
    // setup will be called before GUI has been initialized.
    // I mean, it *should not* happen, but better safe than boot loop.
    ESP_LOGW(TAG, "Failed to get screen pointer");
    return;
  }
  this->obj = lv_label_create(screen);
  this->update();
}
void GuiLabel::loop() {}
void GuiLabel::dump_config() {
  if (this->obj == nullptr) return;

  ESP_LOGCONFIG(TAG, "Label created at (%i, %i)", this->x_, this->y_);
}

void GuiLabel::print(const char *text) {
  this->set_text(text);
  this->update();
}
void GuiLabel::print(int x, int y, const char *text) {
  this->set_text(text);
  this->set_coords(x, y);
  this->update();
}

#ifdef USE_TIME
void GuiLabel::strftime(const char *format, ESPTime time) {
  char buffer[64] = {0};
  size_t ret = time.strftime(buffer, sizeof(buffer), format);

  ESP_LOGVV(TAG, "Updating label's text to: %s", buffer);
  ESP_LOGVV(TAG, "\tstrftime result: %i", ret);

  if (ret > 0) {
    this->set_text(buffer);
    this->update();
  }
}
void GuiLabel::strftime(int x, int y, const char *format, ESPTime time) {
  this->strftime(format, time);
  this->update();
}
#endif

/// GUI Checkbox

#ifdef USE_CHECKBOX
void GuiCheckbox::setup() {
  lv_obj_t *screen = GuiObject::setup();
  if (screen == nullptr) {
    ESP_LOGW(TAG, "Failed to get screen pointer");
    return;
  }
  this->obj = lv_checkbox_create(lv_scr_act());

  lv_checkbox_set_text_static(this->obj, this->get_text());
  lv_obj_set_style_text_font(this->obj, &lv_font_montserrat_18,
                             LV_PART_MAIN | LV_STATE_DEFAULT);

  this->switch_state = this->switch_->get_initial_state();
  this->switch_->add_on_state_callback(switch_event_callback);
  lv_obj_add_event_cb(this->obj, this->gui_event_callback,
                      LV_EVENT_VALUE_CHANGED, (void *)this);
  this->update();
}

void GuiCheckbox::loop() {
  bool state = this->switch_->state;
  if (state != this->switch_state) {
    ((state) ? lv_obj_add_state(this->obj, LV_STATE_CHECKED)
             : lv_obj_clear_state(this->obj, LV_STATE_CHECKED));
    this->switch_state = state;
  }
}

void GuiCheckbox::gui_event_callback(lv_event_t *event) {
  lv_obj_t *target = (lv_obj_t *)lv_event_get_target(event);
  GuiCheckbox *sw = (GuiCheckbox *)event->user_data;
  bool state = (lv_obj_get_state(target) & LV_STATE_CHECKED);
}

void GuiCheckbox::switch_event_callback(bool state) {}

void GuiCheckbox::dump_config() {
  ESP_LOGCONFIG(TAG, "Checkbox created at (%i, %i)", this->x_, this->y_);
}
#endif

/// GUI Meter

#ifdef USE_METER
void GuiMeter::setup() {
  lv_obj_t *screen = GuiObject::setup();
  if (screen == nullptr) return;

  lv_obj_t *meter = lv_meter_create(screen);

  lv_obj_set_size(meter, 160, 160);

  /*Add a scale first*/
  lv_meter_scale_t *scale = lv_meter_add_scale(meter);
  lv_meter_set_scale_ticks(meter, scale, 41, 2, 10,
                           lv_palette_main(LV_PALETTE_GREY));
  lv_meter_set_scale_major_ticks(meter, scale, 8, 4, 15, lv_color_black(), 10);
  lv_obj_set_style_text_font(meter, &lv_font_montserrat_18, LV_PART_ANY);

  lv_meter_indicator_t *indic;

  /*Add a blue arc to the start*/
  indic =
      lv_meter_add_arc(meter, scale, 3, lv_palette_main(LV_PALETTE_BLUE), 0);
  lv_meter_set_indicator_start_value(meter, indic, 0);
  lv_meter_set_indicator_end_value(meter, indic, 20);

  /*Make the tick lines blue at the start of the scale*/
  indic =
      lv_meter_add_scale_lines(meter, scale, lv_palette_main(LV_PALETTE_BLUE),
                               lv_palette_main(LV_PALETTE_BLUE), false, 0);
  lv_meter_set_indicator_start_value(meter, indic, 0);
  lv_meter_set_indicator_end_value(meter, indic, 20);

  /*Add a red arc to the end*/
  indic = lv_meter_add_arc(meter, scale, 3, lv_palette_main(LV_PALETTE_RED), 0);
  lv_meter_set_indicator_start_value(meter, indic, 80);
  lv_meter_set_indicator_end_value(meter, indic, 100);

  /*Make the tick lines red at the end of the scale*/
  indic =
      lv_meter_add_scale_lines(meter, scale, lv_palette_main(LV_PALETTE_RED),
                               lv_palette_main(LV_PALETTE_RED), false, 0);
  lv_meter_set_indicator_start_value(meter, indic, 80);
  lv_meter_set_indicator_end_value(meter, indic, 100);

  /*Add a needle line indicator*/
  indic = lv_meter_add_needle_line(meter, scale, 4,
                                   lv_palette_main(LV_PALETTE_GREY), -10);

  this->obj = std::move(meter);
  this->update();
}
void GuiMeter::loop() {}
void GuiMeter::dump_config() {}
#endif

}  // namespace gui
}  // namespace esphome
