
> [!IMPORTANT]
> [@clydebarrow](https://github.com/clydebarrow)'s fine work on `lvgl` component is now merged into [upstream ESPHome](https://esphome.io/components/lvgl/)!
> This project is now redundant, so as of Oct 21st 2024 it is archived. 📦

# ESPHome GUI Component

- [ESPHome GUI Component](#esphome-gui-component)
- [Overview](#overview)
- [Status](#status)
  - [Known Issues](#known-issues)
- [Usage](#usage)
- [Reference](#reference)
  - [GUI Setup](#gui-setup)
  - [GUI Objects](#gui-objects)
    - [Label](#label)
    - [Checkbox](#checkbox)
  - [Custom `display` Component](#custom-display-component)

# Overview

`esphome-gui` is an **external component for [ESPHome](https://esphome.io)** which provides a way for building **Graphical User Interface for ESPHome**-based projects. Initially inspired by @fvanroie's [esphome-lvgl](https://github.com/fvanroie/esphome-lvgl).

![esphome-gui on a LilyGO T-Embed board](docs/assets/esphome-gui-tembed-lilygo.jpg)

Slightly modified [display component](https://esphome.io/components/display/) from ESPHome is required by `esphome-gui` but it does not need any additional 3rd party SPI drivers. Communication with display devices is handled by ESPHome which -- in theory -- means that all of the displays supported by ESPHome are automatically available for use with `esphome-gui`.

Internally `esphome-gui` relies on [LVGL](https://lvgl.io) library to do all the rendering. So, one might think of this component as an abstraction layer which exposes `lvgl` objects to ESPHome infrastructure.

Idea is to allow for defining GUI elements (or widgets) directly in YAML...

```yaml
gui:
  id: mygui
  display_id: disp
  widgets:
    - label:
        id: mylabel
        position: 40, 100
        dimensions: 100x25
```
...and let ESPHome do its thing:

```yaml
time:
  - platform: homeassistant
    id: home_time
    on_time:
      - seconds: 0
        minutes: /1
        then:
          - lambda: |
              id(mylabel).strftime("%H:%M", id(home_time).now());
```

# Status

This component is on an _**extremely early**_ stage of development and, judging by amount of time I have available, will stay that way for forseeable future.

Still, goal, the treasure at the end of the rainbow 🌈, is an ESPHome GUI component that:
* integrates seamlessly with rest of ESPHome
* requires as little changes in other areas of ESPHome (looking at you, `Display`)
* allows for defining all basic Lvgl objects using YAML
* handles user input, like touchscreens, buttons, etc.
* perhaps even implements [Display Menu Interface](https://esphome.io/components/display_menu/index.html)

Essentially, this would be a replacement and/or supplement for ESPHome's rendering engine. Where is that component now, see for yourself 😬.

There's a lot of activity around ESPHome and `lvgl` going on as of late, especially
`@clydebarrow`'s work on building [`lvgl` component](https://github.com/clydebarrow/esphome/tree/lvgl). To avoid excessive overlap and not-invented-here syndrome,
I'm starting to shift towards re-using his work there. Hopefully, we'll just merge
it all together and have a single component in ESPHome 🤞🏻.

## Known Issues

1. Weird things happen when display rotation is enabled.

# Usage

First off, you need to define repository with external components in your project:

```yaml
external_components:
  - source:
      type: git
      url: https://github.com/lukasz-tuz/esphome-gui
      ref: main
    components: [ display, gui ]
```

See [ESPHome external components documentation](https://esphome.io/components/external_components.html) for more information.

After that, `esphome-gui` is used in a usual fashion:

```yaml
gui:
  id: mygui
  display_id: disp
  widgets:
    ...
```

Check the [reference](#reference) for full description of the configuration variables.

Note that GUI component requires that a `display` is defined in the configuration as well. Since `display` should be on the list of external components, implementation from this repo will take precedence over built-in one. However, there is only one change to how custom `display` is configured vs. the regular one - `lambda` is no longer required:

```yaml
# Example display configuration for use with gui
display:
  - platform: st7789v
    model: CUSTOM
    auto_clear_enabled: False
    eightbitcolor: False
    update_interval: 10s
    rotation: 0
    width: 170
    height: 320
    offset_width: 0
    offset_height: 35
    backlight_pin: GPIO15
    cs_pin: GPIO10
    dc_pin: GPIO13
    reset_pin: GPIO9
    id: disp

```

# Reference

## GUI Setup

Main `gui` object establishes connection between ESPHome's `Display` object and `lvgl` library.

```yaml
gui:
  id: mygui
  display_id: disp
  items:
    ...
```

| Configuration | Values | Required? | Description                                                              |
| ------------- | ------ | --------- | ------------------------------------------------------------------------ |
| `id`          | string | required  | Unique ID for your GUI                                                   |
| `display_id`  | string | required  | ID of `display` object which will be used alongside with GUI             |
| `widgets`     | list   | required  | List of GUI elements. See [GUI Objects](#gui-objects) for full reference |


## GUI Objects

GUI objects (or elements, widgets, items,... I should really settle on one name...) are created under `widgets` list in GUI configuration.

```yaml
gui:
  id: mygui
  display_id: disp
  widgets:
    - label:
        id: mylabel
        position: 40, 100
        dimensions: 100x25
    - checkbox:
        id: myswitch
        position: 0,0
        dimensions: 170x25
        switch_id: power_on
```

Set of available configuration variables largely depends on the item itself, but there is a set of common options.

| Configuration | Values                     | Required? | Description                                                                                            |
| ------------- | -------------------------- | --------- | ------------------------------------------------------------------------------------------------------ |
| `id`          | string                     | required  | Unique ID for the item                                                                                 |
| `position`    | `X, Y`                     | required  | coordinates of top-left corner of the item on screen. `0, 0` is at the top-left corner of the display. |
| `dimensions`  | `WxH`                      | required  | width and height of the item in pixes, following `WxH` format.                                         |

`GuiObject` class comes with a few public methods for accessing basic parameters of an object:

```cpp
  void update();
  void set_coords(int x, int y);
  void set_dimensions(int w, int h);
  void set_text(const char* val) { this->text_ = val; }
  inline const char* get_text() { return this->text_.c_str(); }
```

`GuiObject` holds common parameter for all types of GUI elements: coordinates (GUI element has to be shown _somewhere_), dimensions (be careful not to set them to `0x0`), label (many of the elements have a label of some sort). However, `update()` method needs to be called to convey these settings to lvgl backend.

### Label

> It prints text and stuff.

```yaml
gui:
  id: mygui
  display_id: disp
  items:
    - label:
        id: mylabel
        position: 40, 100
        dimensions: 100x25
```

| Configuration | Values | Required? | Description            |
| ------------- | ------ | --------- | ---------------------- |
| `text`        | string | optional  | Static text to display |

Additionally, `label` objects can be modified directly through lambdas. `GuiLabel` class implements a few helper methods for updating text and/or coordinates of the label:

```cpp
  void print(const char* text);
  void print(int x, int y, const char* text);
  void strftime(const char* format, time::ESPTime time);
  void strftime(int x, int y, const char* format, time::ESPTime time);
```

Example of usage can be found under [docs/examples](docs/examples/), fragment pasted here for convenience.

```yaml
time:
  - platform: homeassistant
    id: home_time
    on_time:
      - seconds: 0
        minutes: /1
        then:
          - lambda: |
              id(mylabel).strftime("%H:%M", id(home_time).now());
    on_time_sync: 
      then:
        - lambda: |
            id(mylabel).strftime("%H:%M", id(home_time).now());
```

### Checkbox

> Since no user input handling is there, yet, it can display state of a switch.

```yaml
gui:
  id: mygui
  display_id: disp
  items:
    - checkbox:
        id: myswitch
        position: 0,0
        dimensions: 170x25
        switch_id: power_on
```

| Configuration | Values | Required? | Description            |
| ------------- | ------ | --------- | ---------------------- |
| `text`        | string | optional  | Label for the checkbox |
| `switch_id`   | string | required  | ID of an existing switch which should be mirrored by the checkbox |

Once instantiated, `GuiCheckbox` object will monitor state of linked switch in the `loop()` method. This will be changed in the future so that asynchronous events are used in favor of polling.

## Custom `display` Component

GUI component requires that a custom `Display` implementation is used instead of the stock one. Changes are kept to a minimum and are there only to have lvgl use the memory buffer allocated by `display`. This way, lvgl renders the components to the display buffer and uses ESPHome's SPI drivers to write contents of that buffer to a display.

All changes in the Display's code are ifdef'd with `USE_GUI` flag.

> **Warning**
>
> If both `gui` and ESPHome's built-in rendering engine are used at the same time, results can be unexpected. Most likely, there will be a random pattern displayed on the screen.
