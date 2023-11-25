import re

import esphome.codegen as cg
import esphome.config_validation as cv
import esphome.core as core
from esphome.schema_extractors import schema_extractor, SCHEMA_EXTRACT
from esphome.components import display, switch, sensor, image, color

from esphome.const import (
    CONF_ID,
    CONF_VALUE,
    CONF_RANGE_FROM,
    CONF_RANGE_TO,
    CONF_COLOR,
    CONF_MIN_VALUE,
    CONF_MAX_VALUE,
    CONF_MODE,
    CONF_WIDTH,
    CONF_SENSOR,
    CONF_BINARY_SENSOR,
    CONF_GROUP,
    CONF_LENGTH,
    CONF_COUNT,
)

CODEOWNERS = ["@lukasz-tuz"]

# Contains _extensive_ amount of code from @clydebarrow's work on lvgl component
# for ESPHome. Since both this component and his lvgl component both intend
# to serve the same purpose, they will probably merge into one at some point
# in the future. For now, I'm re-using his schema to avoid reinventing the wheel.

DEPENDENCIES = ["display"]

CONF_DISPLAY_ID = "display_id"
CONF_SWITCH_ID = "switch_id"
CONF_CHECKBOX = "checkbox"
CONF_DESCRIPTION = "description"
CONF_DIMENSIONS = "dimensions"
CONF_POSITION = "position"

#
# @clydebarrow lvgl component
#
CONF_ADJUSTABLE = "adjustable"
CONF_ANGLE_RANGE = "angle_range"
CONF_ANIMATED = "animated"
CONF_ARC = "arc"
CONF_BACKGROUND_STYLE = "background_style"
CONF_BAR = "bar"
CONF_BTN = "btn"
CONF_BYTE_ORDER = "byte_order"
CONF_CHANGE_RATE = "change_rate"
CONF_CLEAR_FLAGS = "clear_flags"
CONF_COLOR_DEPTH = "color_depth"
CONF_COLOR_END = "color_end"
CONF_COLOR_START = "color_start"
CONF_CRITICAL_VALUE = "critical_value"
CONF_DEFAULT = "default"
CONF_DISPLAY_ID = "display_id"
CONF_END_ANGLE = "end_angle"
CONF_END_VALUE = "end_value"
CONF_FLEX_FLOW = "flex_flow"
CONF_IMG = "img"
CONF_INDICATORS = "indicators"
CONF_LABEL = "label"
CONF_LABEL_GAP = "label_gap"
CONF_LAYOUT = "layout"
CONF_LINE = "line"
CONF_LINE_WIDTH = "line_width"
CONF_LOCAL = "local"
CONF_LOG_LEVEL = "log_level"
CONF_LVGL_COMPONENT = "lvgl_component"
CONF_LVGL_ID = "lvgl_id"
CONF_MAIN = "main"
CONF_MAJOR = "major"
CONF_METER = "meter"
CONF_OBJ = "obj"
CONF_OBJ_ID = "obj_id"
CONF_PIVOT_X = "pivot_x"
CONF_PIVOT_Y = "pivot_y"
CONF_POINTS = "points"
CONF_ROTARY_ENCODERS = "rotary_encoders"
CONF_ROTATION = "rotation"
CONF_R_MOD = "r_mod"
CONF_SCALES = "scales"
CONF_SCALE_LINES = "scale_lines"
CONF_SET_FLAGS = "set_flags"
CONF_SLIDER = "slider"
CONF_SRC = "src"
CONF_START_ANGLE = "start_angle"
CONF_START_VALUE = "start_value"
CONF_STATES = "states"
CONF_STRIDE = "stride"
CONF_STYLE = "style"
CONF_STYLES = "styles"
CONF_STYLE_DEFINITIONS = "style_definitions"
CONF_STYLE_ID = "style_id"
CONF_TEXT = "text"
CONF_TICKS = "ticks"
CONF_TOUCHSCREENS = "touchscreens"
CONF_WIDGETS = "widgets"

LOG_LEVELS = [
    "TRACE",
    "INFO",
    "WARN",
    "ERROR",
    "USER",
    "NONE",
]
STATES = [
    CONF_DEFAULT,
    "checked",
    "focused",
    "edited",
    "hovered",
    "pressed",
    "disabled",
]

PARTS = [
    "main",
    "scrollbar",
    "indicator",
    "knob",
    "selected",
    "items",
    "ticks",
    "cursor",
]

ALIGNMENTS = [
    "TOP_LEFT",
    "TOP_MID",
    "TOP_RIGHT",
    "LEFT_MID",
    "CENTER",
    "RIGHT_MID",
    "BOTTOM_LEFT",
    "BOTTOM_MID",
    "BOTTOM_RIGHT",
    "OUT_LEFT_TOP",
    "OUT_TOP_LEFT",
    "OUT_TOP_MID",
    "OUT_TOP_RIGHT",
    "OUT_RIGHT_TOP",
    "OUT_LEFT_MID",
    "OUT_CENTER",
    "OUT_RIGHT_MID",
    "OUT_LEFT_BOTTOM",
    "OUT_BOTTOM_LEFT",
    "OUT_BOTTOM_MID",
    "OUT_BOTTOM_RIGHT",
    "OUT_RIGHT_BOTTOM",
]

FLEX_FLOWS = [
    "ROW",
    "COLUMN",
    "ROW_WRAP",
    "COLUMN_WRAP",
    "ROW_REVERSE",
    "COLUMN_REVERSE",
    "ROW_WRAP_REVERSE",
    "COLUMN_WRAP_REVERSE",
]

OBJ_FLAGS = [
    "hidden",
    "clickable",
    "click_focusable",
    "checkable",
    "scrollable",
    "scroll_elastic",
    "scroll_momentum",
    "scroll_one",
    "scroll_chain_hor",
    "scroll_chain_ver",
    "scroll_chain",
    "scroll_on_focus",
    "scroll_with_arrow",
    "snappable",
    "press_lock",
    "event_bubble",
    "gesture_bubble",
    "adv_hittest",
    "ignore_layout",
    "floating",
    "overflow_visible",
    "layout_1",
    "layout_2",
    "widget_1",
    "widget_2",
    "user_1",
    "user_2",
    "user_3",
    "user_4",
]

ARC_MODES = ["NORMAL", "REVERSE", "SYMMETRICAL"]
BAR_MODES = ["NORMAL", "SYMMETRICAL", "RANGE"]

# List of other components used
lvgl_components_required = set()


def requires_component(comp):
    def validator(value):
        lvgl_components_required.add(comp)
        return cv.requires_component(comp)(value)

    return validator


def lv_color(value):
    if isinstance(value, int):
        hexval = cv.hex_int(value)
        return f"lv_color_hex({hexval})"
    color_id = cv.use_id(color)(value)
    return f"lv_color_from({color_id})"


# List the LVGL built-in fonts that are available
LV_FONTS = list(map(lambda size: f"montserrat_{size}", range(12, 50, 2))) + [
    "montserrat_12_subpx",
    "montserrat_28_compressed",
    "dejavu_16_persian_hebrew",
    "simsun_16_cjk16",
    "unscii_8",
    "unscii_16",
]

# Record those we actually use
lv_fonts_used = set()


def lv_font(value):
    """Accept either the name of a built-in LVGL font, or the ID of an ESPHome font"""
    global lv_fonts_used
    if value == SCHEMA_EXTRACT:
        return LV_FONTS
    if isinstance(value, str) and value.lower() in LV_FONTS:
        font = cv.one_of(*LV_FONTS, lower=True)(value)
        lv_fonts_used.add(font)
        return "&lv_font_" + font
    font = cv.use_id(Font)(value)
    return f"(new lvgl::FontEngine({font}))->get_lv_font()"


def lv_bool(value):
    if cv.boolean(value):
        return "true"
    return "false"


def lv_prefix(value, choices, prefix):
    if value.startswith(prefix):
        return cv.one_of(*list(map(lambda v: prefix + v, choices)), upper=True)(value)
    return prefix + cv.one_of(*choices, upper=True)(value)


def lv_animated(value):
    if isinstance(value, bool):
        value = "ON" if value else "OFF"
    return lv_one_of(["OFF", "ON"], "LV_ANIM_")(value)


def lv_one_of(choices, prefix):
    """Allow one of a list of choices, mapped to upper case, and prepend the choice with the prefix.
    It's also permitted to include the prefix in the value"""

    @schema_extractor("one_of")
    def validator(value):
        if value == SCHEMA_EXTRACT:
            return choices
        return lv_prefix(value, choices, prefix)

    return validator


def lv_any_of(choices, prefix):
    """Allow any of a list of choices, mapped to upper case, and prepend the choice with the prefix.
    It's also permitted to include the prefix in the value"""

    @schema_extractor("one_of")
    def validator(value):
        if value == SCHEMA_EXTRACT:
            return choices
        return "|".join(
            map(
                lambda v: "(int)" + lv_prefix(v, choices, prefix), cv.ensure_list(value)
            )
        )

    return validator


def pixels_or_percent(value):
    """A length in one axis - either a number (pixels) or a percentage"""
    if isinstance(value, int):
        return str(cv.int_(value))
    # Will throw an exception if not a percentage.
    return f"lv_pct({int(cv.percentage(value) * 100)})"


def lv_zoom(value):
    value = cv.float_range(0.1, 10.0)(value)
    return int(value * 256)


def lv_angle(value):
    return cv.float_range(0.0, 360.0)(cv.angle(value))


@schema_extractor("one_of")
def lv_size(value):
    """A size in one axis - one of "size_content", a number (pixels) or a percentage"""
    if value == SCHEMA_EXTRACT:
        return ["size_content", "pixels", "..%"]
    if isinstance(value, str) and not value.endswith("%"):
        if value.upper() == "SIZE_CONTENT":
            return "LV_SIZE_CONTENT"
        raise cv.Invalid("must be 'size_content', a pixel position or a percentage")
    if isinstance(value, int):
        return str(cv.int_(value))
    # Will throw an exception if not a percentage.
    return f"lv_pct({int(cv.percentage(value) * 100)})"


def lv_opacity(value):
    value = cv.Any(cv.percentage, lv_one_of(["TRANSP", "COVER"], "LV_OPA_"))(value)
    if isinstance(value, str):
        return value
    return int(value * 255)


def lv_stop_value(value):
    return cv.int_range(0, 255)


STYLE_PROPS = {
    "align": lv_one_of(ALIGNMENTS, "LV_ALIGN_"),
    "arc_opa": lv_opacity,
    "arc_color": lv_color,
    "arc_rounded": lv_bool,
    "arc_width": cv.positive_int,
    "bg_color": lv_color,
    "bg_grad_color": lv_color,
    "bg_dither_mode": lv_one_of(["NONE", "ORDERED", "ERR_DIFF"], "LV_DITHER_"),
    "bg_grad_dir": lv_one_of(["NONE", "HOR", "VER"], "LV_GRAD_DIR_"),
    "bg_grad_stop": lv_stop_value,
    "bg_img_opa": lv_opacity,
    "bg_img_recolor": lv_color,
    "bg_img_recolor_opa": lv_opacity,
    "bg_main_stop": lv_stop_value,
    "bg_opa": lv_opacity,
    "border_color": lv_color,
    "border_opa": lv_opacity,
    "border_post": cv.boolean,
    "border_side": lv_any_of(
        ["NONE", "TOP", "BOTTOM", "LEFT", "RIGHT", "INTERNAL"], "LV_BORDER_SIDE_"
    ),
    "border_width": cv.positive_int,
    "clip_corner": lv_bool,
    "height": lv_size,
    "line_width": cv.positive_int,
    "line_dash_width": cv.positive_int,
    "line_dash_gap": cv.positive_int,
    "line_rounded": lv_bool,
    "line_color": lv_color,
    "opa": lv_opacity,
    "opa_layered": lv_opacity,
    "outline_color": lv_color,
    "outline_opa": lv_opacity,
    "outline_pad": cv.positive_int,
    "outline_width": cv.positive_int,
    "pad_all": cv.positive_int,
    "pad_bottom": cv.positive_int,
    "pad_column": cv.positive_int,
    "pad_left": cv.positive_int,
    "pad_right": cv.positive_int,
    "pad_row": cv.positive_int,
    "pad_top": cv.positive_int,
    "shadow_color": lv_color,
    "shadow_ofs_x": cv.int_,
    "shadow_ofs_y": cv.int_,
    "shadow_opa": lv_opacity,
    "shadow_spread": cv.int_,
    "shadow_width": cv.positive_int,
    "text_align": lv_one_of(["LEFT", "CENTER", "RIGHT", "AUTO"], "LV_TEXT_ALIGN_"),
    "text_color": lv_color,
    "text_decor": lv_any_of(["NONE", "UNDERLINE", "STRIKETHROUGH"], "LV_TEXT_DECOR_"),
    "text_font": lv_font,
    "text_letter_space": cv.positive_int,
    "text_line_space": cv.positive_int,
    "text_opa": lv_opacity,
    "transform_angle": lv_angle,
    "transform_height": pixels_or_percent,
    "transform_pivot_x": pixels_or_percent,
    "transform_pivot_y": pixels_or_percent,
    "transform_zoom": lv_zoom,
    "translate_x": pixels_or_percent,
    "translate_y": pixels_or_percent,
    "max_height": pixels_or_percent,
    "max_width": pixels_or_percent,
    "min_height": pixels_or_percent,
    "min_width": pixels_or_percent,
    "radius": cv.Any(cv.positive_int, lv_one_of(["CIRCLE"], "LV_RADIUS_")),
    "width": lv_size,
    "x": pixels_or_percent,
    "y": pixels_or_percent,
}

# Create a schema from a list of optional properties
PROP_SCHEMA = cv.Schema({cv.Optional(k): v for k, v in STYLE_PROPS.items()})


def generate_id(base):
    generate_id.counter += 1
    return f"lvgl_{base}_{generate_id.counter}"


generate_id.counter = 0


def cv_int_list(il):
    nl = il.replace(" ", "").split(",")
    return list(map(lambda x: int(x), nl))


def cv_point_list(value):
    if not isinstance(value, list):
        raise cv.Invalid("List of points required")
    values = list(map(cv_int_list, value))
    for v in values:
        if (
            not isinstance(v, list)
            or not len(v) == 2
            or not isinstance(v[0], int)
            or not isinstance(v[1], int)
        ):
            raise cv.Invalid("Points must be a list of x,y integer pairs")
    return {
        CONF_ID: cv.declare_id(lv_point_t)(generate_id(CONF_POINTS)),
        CONF_POINTS: values,
    }


def container_schema(lv_type, extras=None):
    schema = OBJ_SCHEMA
    if extras is not None:
        schema = schema.extend(extras).add_extra(validate_max_min)
    schema = schema.extend({cv.GenerateID(): cv.declare_id(lv_type)})
    """Delayed evaluation for recursion"""

    def validator(value):
        widgets = cv.Schema(
            {
                cv.Optional(CONF_WIDGETS): cv.ensure_list(WIDGET_SCHEMA),
            }
        )
        return schema.extend(widgets)(value)

    return validator


def validate_max_min(config):
    if CONF_MAX_VALUE in config and CONF_MIN_VALUE in config:
        if config[CONF_MAX_VALUE] <= config[CONF_MIN_VALUE]:
            raise cv.Invalid("max_value must be greater than min_value")
    return config


def lv_value(value):
    if isinstance(value, int):
        return cv.float_(float(cv.int_(value)))
    if isinstance(value, float):
        return cv.float_(value)
    return cv.templatable(cv.use_id(Sensor))(value)


def lv_text_value(value):
    if isinstance(value, cv.Lambda):
        return cv.returning_lambda(value)
    if isinstance(value, core.ID):
        return cv.use_id(Sensor)(value)
    return cv.string(value)


#
# @clydebarrow lvgl component ends
#
# Following code for component schema also leverages the lvgl component,
# but it's not a direct copy-paste.
#


gui_ns = cg.esphome_ns.namespace("gui")
GuiComponent = gui_ns.class_("GuiComponent", cg.Component)
GuiObject = gui_ns.class_("GuiObject")
GuiLabel = gui_ns.class_("GuiLabel", GuiObject, cg.Component)
GuiCheckbox = gui_ns.class_("GuiCheckbox", GuiObject, cg.Component)
GuiMeter = gui_ns.class_("GuiMeter", GuiObject, cg.Component)


def validate_position(position):
    r = re.match(r"^([0-9]*),[ ]*([0-9]*)", position)
    if r is None:
        raise cv.Invalid(
            f"{CONF_POSITION}: has to specify x and y coordinates delimited by a comma, '{position}' provided"
        )
    else:
        x, y = r.groups()
        return [int(x), int(y)]


INDICATOR_SCHEMA = cv.Any(
    # {
    #     cv.Exclusive(CONF_LINE, CONF_INDICATORS): cv.Schema(
    #         {
    #             cv.GenerateID(): cv.declare_id(lv_meter_indicator_t),
    #             cv.Optional(CONF_WIDTH, default=4): lv_size,
    #             cv.Optional(CONF_COLOR, default=0): lv_color,
    #             cv.Optional(CONF_R_MOD, default=0): lv_size,
    #             cv.Optional(CONF_VALUE): lv_value,
    #         }
    #     ),
    #     cv.Exclusive(CONF_IMG, CONF_INDICATORS): cv.Schema(
    #         {
    #             cv.GenerateID(): cv.declare_id(lv_meter_indicator_t),
    #             cv.Optional(CONF_PIVOT_X, default=0): lv_size,
    #             cv.Optional(CONF_PIVOT_X, default="50%"): lv_size,
    #             cv.Optional(CONF_VALUE): lv_value,
    #         }
    #     ),
    #     cv.Exclusive(CONF_ARC, CONF_INDICATORS): cv.Schema(
    #         {
    #             cv.GenerateID(): cv.declare_id(lv_meter_indicator_t),
    #             cv.Optional(CONF_WIDTH, default=4): lv_size,
    #             cv.Optional(CONF_COLOR, default=0): lv_color,
    #             cv.Optional(CONF_R_MOD, default=0): lv_size,
    #             cv.Exclusive(CONF_VALUE, CONF_VALUE): lv_value,
    #             cv.Exclusive(CONF_START_VALUE, CONF_VALUE): lv_value,
    #             cv.Optional(CONF_END_VALUE): lv_value,
    #         }
    #     ),
    #     cv.Exclusive(CONF_TICKS, CONF_INDICATORS): cv.Schema(
    #         {
    #             cv.GenerateID(): cv.declare_id(lv_meter_indicator_t),
    #             cv.Optional(CONF_WIDTH, default=4): lv_size,
    #             cv.Optional(CONF_COLOR_START, default=0): lv_color,
    #             cv.Optional(CONF_COLOR_END): lv_color,
    #             cv.Optional(CONF_R_MOD, default=0): lv_size,
    #             cv.Exclusive(CONF_VALUE, CONF_VALUE): lv_value,
    #             cv.Exclusive(CONF_START_VALUE, CONF_VALUE): lv_value,
    #             cv.Optional(CONF_END_VALUE): lv_value,
    #             cv.Optional(CONF_LOCAL, default=False): lv_bool,
    #         }
    #     ),
    # }
)

SCALE_SCHEMA = cv.Schema(
    {
        cv.Optional(CONF_TICKS): cv.Schema(
            {
                cv.Optional(CONF_COUNT, default=12): cv.positive_int,
                cv.Optional(CONF_WIDTH, default=2): lv_size,
                cv.Optional(CONF_LENGTH, default=10): lv_size,
                cv.Optional(CONF_COLOR, default=0x808080): lv_color,
                cv.Optional(CONF_MAJOR): cv.Schema(
                    {
                        cv.Optional(CONF_STRIDE, default=3): cv.positive_int,
                        cv.Optional(CONF_WIDTH, default=5): lv_size,
                        cv.Optional(CONF_LENGTH, default="15%"): lv_size,
                        cv.Optional(CONF_COLOR, default=0): lv_color,
                        cv.Optional(CONF_LABEL_GAP, default=4): lv_size,
                    }
                ),
            }
        ),
        cv.Optional(CONF_RANGE_FROM, default=0.0): cv.float_,
        cv.Optional(CONF_RANGE_TO, default=100.0): cv.float_,
        cv.Optional(CONF_ANGLE_RANGE, default=270): cv.int_range(0, 360),
        cv.Optional(CONF_ROTATION): lv_angle,
        cv.Optional(CONF_INDICATORS): cv.ensure_list(INDICATOR_SCHEMA),
    }
)

ARC_SCHEMA = cv.Schema(
    {
        cv.Optional(CONF_VALUE): lv_value,
        cv.Optional(CONF_MIN_VALUE, default=0): cv.int_,
        cv.Optional(CONF_MAX_VALUE, default=100): cv.int_,
        cv.Optional(CONF_START_ANGLE, default=135): lv_angle,
        cv.Optional(CONF_END_ANGLE, default=45): lv_angle,
        cv.Optional(CONF_ROTATION, default=0.0): lv_angle,
        cv.Optional(CONF_ADJUSTABLE, default=False): bool,
        cv.Optional(CONF_MODE, default="NORMAL"): lv_one_of(ARC_MODES, "LV_ARC_MODE_"),
        cv.Optional(CONF_CHANGE_RATE, default=720): cv.uint16_t,
    }
)

BAR_SCHEMA = cv.Schema(
    {
        cv.Optional(CONF_VALUE): lv_value,
        cv.Optional(CONF_MIN_VALUE, default=0): cv.int_,
        cv.Optional(CONF_MAX_VALUE, default=100): cv.int_,
        cv.Optional(CONF_MODE, default="NORMAL"): lv_one_of(BAR_MODES, "LV_BAR_MODE_"),
        cv.Optional(CONF_ANIMATED, default=True): lv_animated,
    }
)

STYLE_SCHEMA = PROP_SCHEMA.extend(
    {
        cv.Optional(CONF_STYLES): cv.Any(),  # cv.ensure_list(cv.use_id(lv_style_t)),
    }
)
STATE_SCHEMA = cv.Schema({cv.Optional(state): STYLE_SCHEMA for state in STATES}).extend(
    STYLE_SCHEMA
)
PART_SCHEMA = cv.Schema({cv.Optional(part): STATE_SCHEMA for part in PARTS}).extend(
    STATE_SCHEMA
)
FLAG_SCHEMA = cv.Schema({cv.Optional(flag): cv.boolean for flag in OBJ_FLAGS})
FLAG_LIST = cv.ensure_list(lv_one_of(OBJ_FLAGS, "LV_OBJ_FLAG_"))


OBJ_SCHEMA = PART_SCHEMA.extend(FLAG_SCHEMA).extend(
    cv.Schema(
        {
            cv.Optional(CONF_DIMENSIONS): cv.dimensions,
            cv.Optional(CONF_POSITION): validate_position,
            # cv.Optional(CONF_LAYOUT): lv_one_of(["FLEX", "GRID"], "LV_LAYOUT_"),
            # cv.Optional(CONF_FLEX_FLOW, default="ROW_WRAP"): lv_one_of(
            #     FLEX_FLOWS, prefix="LV_FLEX_FLOW_"
            # ),
            cv.Optional(CONF_SET_FLAGS): FLAG_LIST,
            cv.Optional(CONF_CLEAR_FLAGS): FLAG_LIST,
        }
    )
)

WIDGET_SCHEMA = cv.Any(
    {
        cv.Exclusive(CONF_LABEL, CONF_WIDGETS): OBJ_SCHEMA.extend(
            {
                cv.GenerateID(CONF_ID): cv.declare_id(GuiLabel),
                cv.Optional(CONF_TEXT): cv.string,
            }
        ),
        # cv.Exclusive(CONF_LINE, CONF_WIDGETS): OBJ_SCHEMA.extend(
        #     {cv.Required(CONF_POINTS): cv_point_list}
        # ),
        # cv.Exclusive(CONF_ARC, CONF_WIDGETS): OBJ_SCHEMA.extend(ARC_SCHEMA),
        cv.Exclusive(CONF_METER, CONF_WIDGETS): OBJ_SCHEMA.extend(
            {
                cv.GenerateID(CONF_ID): cv.declare_id(GuiMeter),
                cv.Optional(CONF_SCALES): cv.ensure_list(SCALE_SCHEMA),
            }
        ),
        cv.Exclusive(CONF_CHECKBOX, CONF_WIDGETS): OBJ_SCHEMA.extend(
            {
                cv.GenerateID(CONF_ID): cv.declare_id(GuiCheckbox),
                cv.Optional(CONF_TEXT): cv.string,
                cv.GenerateID(CONF_SWITCH_ID): cv.use_id(switch.Switch),
            }
        ),
        # cv.Exclusive(CONF_IMG, CONF_WIDGETS): OBJ_SCHEMA.extend(
        #     {cv.Required(CONF_SRC): cv.use_id(Image_)},
        # ),
    }
)

# Top-level schema from lvgl component has essentially the same structure
# as esphome-gui's. Different names are used, but idea remains.
CONFIG_SCHEMA = cv.COMPONENT_SCHEMA.extend(OBJ_SCHEMA).extend(
    {
        cv.GenerateID(): cv.declare_id(GuiComponent),
        cv.GenerateID(CONF_DISPLAY_ID): cv.use_id(display.DisplayBuffer),
        cv.Optional(CONF_COLOR_DEPTH, default=8): cv.one_of(1, 8, 16, 32),
        cv.Optional(CONF_BYTE_ORDER, default="big_endian"): cv.one_of(
            "big_endian", "little_endian"
        ),
        # Temporarily disabling style definitions until there's a proper
        # class in place to wrap all lvgl's properties in a single object.
        # cv.Optional(CONF_STYLE_DEFINITIONS): cv.ensure_list(
        #     cv.Schema({cv.Required(CONF_ID): cv.declare_id(lv_style_t)})
        #     .extend(PROP_SCHEMA)
        #     .extend(STATE_SCHEMA)
        # ),
        cv.Required(CONF_WIDGETS): cv.ensure_list(WIDGET_SCHEMA),
    }
)

lv_uses = {
    "USER_DATA",
    "LOG",
}


async def build_label(obj, config):
    lv_uses.add("LABEL")
    if CONF_TEXT in config:
        cg.add(obj.set_text(config[CONF_TEXT]))


async def build_checkbox(obj, config):
    lv_uses.add("CHECKBOX")
    sw = await cg.get_variable(config[CONF_SWITCH_ID])
    if CONF_TEXT in config:
        cg.add(obj.set_text(config[CONF_TEXT]))
    cg.add(obj.set_switch(sw))
    cg.add_define("USE_CHECKBOX")


async def build_meter(obj, config):
    lv_uses.add("METER")
    cg.add_define("USE_METER")


GUI_OBJECT_BUILDERS = {
    CONF_LABEL: build_label,
    CONF_CHECKBOX: build_checkbox,
    CONF_METER: build_meter,
}


async def widget_to_code(widget):
    for widget_type, widget_data in widget.items():
        obj = cg.new_Pvariable(widget_data[CONF_ID])
        await cg.register_component(obj, widget_data)

        w, h = widget_data.get(CONF_DIMENSIONS, (0, 0))
        cg.add(obj.set_dimensions(w, h))

        x, y = widget_data.get(CONF_POSITION, (0, 0))
        cg.add(obj.set_coords(x, y))

        if widget_type in GUI_OBJECT_BUILDERS.keys():
            await GUI_OBJECT_BUILDERS[widget_type](obj, widget_data)


async def to_code(config):
    cg.add_library("lvgl/lvgl", "^8.3.9")
    core.CORE.add_build_flag("-DLV_CONF_SKIP=1")
    core.CORE.add_build_flag("-DLV_USE_USER_DATA=1")
    core.CORE.add_build_flag("-DLV_USE_LOG=1")
    # FIXME: Sync with ESPHome's log level
    core.CORE.add_build_flag("-DLV_LOG_LEVEL=LV_LOG_LEVEL_INFO")
    core.CORE.add_build_flag("-DLV_BUILD_EXAMPLES=0")
    core.CORE.add_build_flag("-DLV_USE_DEMO_WIDGETS=0")
    core.CORE.add_build_flag("-DLV_USE_DEMO_KEYPAD_AND_ENCODER=0")
    core.CORE.add_build_flag("-DLV_USE_DEMO_BENCHMARK=0")
    core.CORE.add_build_flag("-DLV_USE_DEMO_STRESS=0")
    core.CORE.add_build_flag("-DLV_USE_DEMO_MUSIC=0")
    core.CORE.add_build_flag("-DLV_TICK_CUSTOM=0")
    core.CORE.add_build_flag("-DLV_MEM_CUSTOM=0")
    core.CORE.add_build_flag("-DLV_DISP_DEF_REFR_PERIOD=30")
    core.CORE.add_build_flag("-DLV_INDEV_DEF_READ_PERIOD=30")
    core.CORE.add_build_flag("-DLV_DPI_DEF=130")
    core.CORE.add_build_flag(f"-DLV_COLOR_DEPTH={config[CONF_COLOR_DEPTH]}")
    if config[CONF_COLOR_DEPTH] == 16:
        if config[CONF_BYTE_ORDER] == "big_endian":
            core.CORE.add_build_flag("-DLV_COLOR_16_SWAP=1")
        else:
            core.CORE.add_build_flag("-DLV_COLOR_16_SWAP=0")
    core.CORE.add_build_flag("-DLV_USE_THEME_DEFAULT=1")
    core.CORE.add_build_flag("-DLV_USE_THEME_BASIC=0")
    core.CORE.add_build_flag("-DLV_USE_THEME_MONO=0")

    for use in lv_uses:
        core.CORE.add_build_flag(f"-DLV_USE_{use}=1")

    # FIXME: Needs proper integration with ESPHome's font component
    core.CORE.add_build_flag("-DLV_FONT_MONTSERRAT_12=1")
    core.CORE.add_build_flag("-DLV_FONT_MONTSERRAT_18=1")
    core.CORE.add_build_flag("-DLV_FONT_MONTSERRAT_36=1")
    core.CORE.add_build_flag("-DLV_FONT_MONTSERRAT_48=1")
    core.CORE.add_build_flag("-DLV_USE_FONT_SUBPX=1")
    core.CORE.add_build_flag("-DLV_FONT_SUBPX_BGR=0")
    core.CORE.add_build_flag("-DLV_FONT_DEFAULT=\\'\\&lv_font_montserrat_36\\'")

    # Disable GPU accelerators for other architectures
    core.CORE.add_build_flag("-DLV_USE_GPU_ARM2D=0")
    core.CORE.add_build_flag("-DLV_USE_GPU_STM32_DMA2D=0")
    core.CORE.add_build_flag("-DLV_USE_GPU_RA6M3_G2D=0")
    core.CORE.add_build_flag("-DLV_USE_GPU_SWM341_DMA2D=0")
    core.CORE.add_build_flag("-DLV_USE_GPU_NXP_PXP=0")
    core.CORE.add_build_flag("-DLV_USE_GPU_NXP_VG_LITE=0")
    core.CORE.add_build_flag("-DLV_USE_GPU_SDL=0")
    core.CORE.add_build_flag("-Isrc")

    gui = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(gui, config)

    disp = await cg.get_variable(config[CONF_DISPLAY_ID])

    cg.add(gui.set_display(disp))

    if CONF_WIDGETS in config:
        for widget in config[CONF_WIDGETS]:
            await widget_to_code(widget)
