import os
import re

import esphome.codegen as cg
import esphome.config_validation as cv
import esphome.core as core
import esphome.core.config as cfg
from esphome.const import CONF_DIMENSIONS, CONF_ID, CONF_POSITION, CONF_TYPE

from esphome.components import display, switch

CODEOWNERS = ["@lukasz-tuz"]

DEPENDENCIES = ["display"]

gui_ns = cg.esphome_ns.namespace("gui")

CONF_DISPLAY_ID = "display_id"
CONF_SWITCH_ID = "switch_id"
CONF_ITEMS = "items"
CONF_LABEL = "label"
CONF_CHECKBOX = "checkbox"
CONF_DESCRIPTION = "description"
CONF_TEXT = "text"


GuiComponent = gui_ns.class_("GuiComponent", cg.Component)
GuiObject = gui_ns.class_("GuiObject")
GuiLabel = gui_ns.class_("GuiLabel", GuiObject, cg.Component)
GuiCheckbox = gui_ns.class_("GuiCheckbox", GuiObject, cg.Component)


def validate_position(position):
    r = re.match(r"^([0-9]*),[ ]*([0-9]*)", position)
    if r is None:
        raise cv.Invalid(
            f"{CONF_POSITION}: has to specify x and y coordinates delimited by a comma, '{position}' provided"
        )
    else:
        x, y = r.groups()
        return [int(x), int(y)]


async def build_label(obj, config):
    if CONF_TEXT in config:
        cg.add(obj.set_text(config[CONF_TEXT]))


async def build_checkbox(obj, config):
    sw = await cg.get_variable(config[CONF_SWITCH_ID])
    if CONF_TEXT in config:
        cg.add(obj.set_text(config[CONF_TEXT]))
    cg.add(obj.set_switch(sw))
    cg.add_define("USE_CHECKBOX")


GUI_OBJECT_BUILDERS = {
    CONF_LABEL: build_label,
    CONF_CHECKBOX: build_checkbox,
}

GUI_ITEM_COMMON_SCHEMA = cv.Schema(
    {
        cv.Required(CONF_DIMENSIONS): cv.dimensions,
        cv.Required(CONF_POSITION): validate_position,
    }
)

GUI_ITEM_SCHEMA = cv.typed_schema(
    {
        CONF_LABEL: GUI_ITEM_COMMON_SCHEMA.extend(
            {
                cv.GenerateID(CONF_ID): cv.declare_id(GuiLabel),
                cv.Optional(CONF_TEXT): cv.string,
            }
        ),
        CONF_CHECKBOX: GUI_ITEM_COMMON_SCHEMA.extend(
            {
                cv.GenerateID(CONF_ID): cv.declare_id(GuiCheckbox),
                cv.Optional(CONF_TEXT): cv.string,
                cv.GenerateID(CONF_SWITCH_ID): cv.use_id(switch.Switch),
            }
        ),
    }
)

GUI_SCHEMA = cv.Schema(
    {
        cv.Required(CONF_ID): cv.declare_id(GuiComponent),
        cv.GenerateID(CONF_DISPLAY_ID): cv.use_id(display.DisplayBuffer),
        cv.Optional(CONF_ITEMS): cv.All(
            cv.ensure_list(GUI_ITEM_SCHEMA),
        ),
    }
)

CONFIG_SCHEMA = cv.All(
    GUI_SCHEMA,
)

# LV_CONF_PATH contains path to modified lv_conf.h, from perspective
# of lv_conf_internal.h. Internal config is under:
# .esphome/build/<project_name>/.piolibdeps/<project_name>/lvgl/src
#
# lv_conf.h gets copied to:
# .esphome/build/<project_name>/src
#
# So LV_CONF_PATH should point three levels up and into the src directory.
# This way ensures that whatever modifications to lv_conf.h will be done
# here, esphome's build picks it up.
LVGL_BUILD_FLAGS = [
    "-D LV_USE_LOG=1",
    "-D LV_USE_DEV_VERSION=0",
]


async def gui_items_to_code(config):
    for item in config:
        obj = cg.new_Pvariable(item[CONF_ID])
        await cg.register_component(obj, item)

        if CONF_DIMENSIONS in item:
            w, h = item[CONF_DIMENSIONS]
            cg.add(obj.set_dimensions(w, h))

        if CONF_POSITION in item:
            x, y = item[CONF_POSITION]
            cg.add(obj.set_coords(x, y))

        if item[CONF_TYPE] in GUI_OBJECT_BUILDERS.keys():
            await GUI_OBJECT_BUILDERS[item[CONF_TYPE]](obj, item)


async def to_code(config):
    whereami = os.path.realpath(__file__)
    component_dir = os.path.dirname(whereami)

    # Make sure that lv_conf.h gets copied to the src directory, along with
    # other generated files.
    lv_conf_path = os.path.join(component_dir, "lv_conf.h")
    core.CORE.add_job(cfg.add_includes, [lv_conf_path])

    cg.add_library("lvgl/lvgl", "^8.3")
    cg.add_platformio_option("build_flags", LVGL_BUILD_FLAGS)
    cg.add_platformio_option("build_flags", ["-D LV_CONF_PATH='" + lv_conf_path + "'"])
    gui = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(gui, config)

    disp = await cg.get_variable(config[CONF_DISPLAY_ID])

    cg.add(gui.set_display(disp))
    cg.add_define("USE_GUI")
    cg.add_define("USE_LVGL_PROD")

    if CONF_ITEMS in config:
        await gui_items_to_code(config[CONF_ITEMS])
