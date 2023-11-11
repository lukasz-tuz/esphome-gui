#include "gui.h"

namespace esphome {
namespace gui {

static const char *const TAG = "gui";

using namespace display;

namespace lv_shim {
static lv_disp_drv_t lv_disp_drv;
static lv_disp_draw_buf_t lv_disp_buf;

static DisplayBuffer *disp_buf{nullptr};

#if LV_USE_LOG
static void lv_esp_log(const char *buf) {
  ESP_LOGV("LVGL", buf);
}
#endif

static void lv_drv_refresh(lv_disp_drv_t *disp_drv, const lv_area_t *area,
                           lv_color_t *buf) {
  lv_shim::disp_buf->update();
  lv_disp_flush_ready(disp_drv);
}

lv_disp_t *init_lv_drv(DisplayBuffer *db, lv_disp_rot_t rotation) {
  lv_shim::disp_buf = db;
  uint8_t *buf = db->get_buffer();

  // hacky hack as there's no consistency in how DisplayBuffer specializations
  // implement get_buffer_length method (if at all)
  uint32_t len = db->get_buffer_length_();
  ESP_LOGV("GUI", "[init_lv_drv] Memory buffer length %u", len);

  lv_init();

#if LV_USE_LOG
  lv_log_register_print_cb(lv_esp_log);
#endif

  lv_disp_draw_buf_init(&lv_disp_buf, buf, NULL, len);
  lv_disp_drv_init(&lv_disp_drv);
  lv_disp_drv.hor_res = disp_buf->get_width();
  lv_disp_drv.ver_res = disp_buf->get_height();
  lv_disp_drv.direct_mode = true;
  lv_disp_drv.full_refresh = false;  // Will trigger the watchdog if set.
  lv_disp_drv.flush_cb = lv_drv_refresh;
  lv_disp_drv.draw_buf = &lv_disp_buf;
  lv_disp_drv.sw_rotate = true;
  lv_disp_t *disp = lv_disp_drv_register(&lv_disp_drv);
  
  lv_obj_set_style_bg_color(lv_scr_act(), lv_color_hex(0x000000), LV_PART_MAIN);
  return disp;
}
}  // namespace lv_shim

void GuiComponent::setup() {
  // Register this instance of the GUI component with the lvgl driver
  DisplayBuffer *disp_buf = this->display_;
  this->lv_disp_ = lv_shim::init_lv_drv(disp_buf, this->get_lv_rotation());
  this->high_freq_.start();
}

void GuiComponent::loop() { lv_timer_handler(); }

void GuiComponent::dump_config() {
  auto drv = this->lv_disp_;
  ESP_LOGCONFIG(TAG, "LVGL driver.hor_res: %i", drv->driver->hor_res);
  ESP_LOGCONFIG(TAG, "LVGL driver.ver_res: %i", drv->driver->ver_res);
  ESP_LOGCONFIG(TAG, "LVGL driver.rotation: %i", drv->driver->rotated);
}

lv_disp_rot_t GuiComponent::get_lv_rotation() {
  if (this->display_ != nullptr) {
    auto rot = this->display_->get_rotation();
    switch (rot) {
      case DISPLAY_ROTATION_0_DEGREES:
        return LV_DISP_ROT_NONE;
      case DISPLAY_ROTATION_90_DEGREES:
        return LV_DISP_ROT_90;
      case DISPLAY_ROTATION_180_DEGREES:
        return LV_DISP_ROT_180;
      case DISPLAY_ROTATION_270_DEGREES:
        return LV_DISP_ROT_270;
    }
  }
  return LV_DISP_ROT_NONE;
}

}  // namespace gui
}  // namespace esphome
