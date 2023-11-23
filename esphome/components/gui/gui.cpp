#include "gui.h"

namespace esphome {
namespace gui {

static const char *const TAG = "gui";
using namespace display;

void GuiComponent::setup() {
#if LV_USE_LOG
  lv_log_register_print_cb(lv_esp_log);
#endif
  uint32_t len = this->display_->get_buffer_length();
  ESP_LOGI(TAG, "[init_lv_drv] Memory buffer length %u", len);

  lv_init();

  lv_disp_draw_buf_init(&this->draw_buf_, this->display_->get_buffer(), NULL,
                        len);
  lv_disp_drv_init(&this->disp_drv_);
  this->disp_drv_.hor_res = this->display_->get_width();
  this->disp_drv_.ver_res = this->display_->get_height();
  this->disp_drv_.direct_mode = true;
  this->disp_drv_.full_refresh = false;  // Will trigger the watchdog if set.
  this->disp_drv_.flush_cb = refresh;
  this->disp_drv_.draw_buf = &this->draw_buf_;
  this->disp_drv_.sw_rotate = true;
  this->disp_drv_.user_data = this;

  lv_disp_ = lv_disp_drv_register(&this->disp_drv_);

  lv_obj_set_style_bg_color(lv_scr_act(), lv_color_hex(0x000000), LV_PART_MAIN);
  this->high_freq_.start();
}

void GuiComponent::loop() { lv_timer_handler(); }

void GuiComponent::dump_config() {
  auto drv = this->lv_disp_;
  ESP_LOGCONFIG(TAG, "LVGL driver.hor_res: %i", drv->driver->hor_res);
  ESP_LOGCONFIG(TAG, "LVGL driver.ver_res: %i", drv->driver->ver_res);
  ESP_LOGCONFIG(TAG, "LVGL driver.rotation: %i", drv->driver->rotated);
}
#if LV_USE_LOG
void GuiComponent::lv_esp_log(const char *buf) {
  esp_log_printf_(ESPHOME_LOG_LEVEL_INFO, TAG, 0, "%s", buf);
}
#endif

void HOT GuiComponent::refresh(lv_disp_drv_t *disp_drv, const lv_area_t *area,
                               lv_color_t *buf) {
  GuiComponent *gui = (GuiComponent *)(disp_drv->user_data);
  gui->refresh_internal_(disp_drv, area, buf);
}

void HOT GuiComponent::refresh_internal_(lv_disp_drv_t *disp_drv,
                                         const lv_area_t *area,
                                         lv_color_t *buf) {
  GuiComponent *gui = (GuiComponent *)(disp_drv->user_data);
  gui->display_->update();
  lv_disp_flush_ready(disp_drv);
}

}  // namespace gui
}  // namespace esphome
