# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#import webrepl
#webrepl.start()

import machine
from machine import Pin
import ili9XXX
import lvgl as lv


bl=machine.Pin(45, machine.Pin.OUT)
bl.value(1)

# 初始化显示
ili9XXX.st7789(
    mosi=6,
    clk=7,
    cs=5,
    dc=4,
    rst=48,
    width=320,
    height=207,
    #start_y=33,
    rot=-3
)

# 初始化LVGL
lv.init()

style_base = lv.style_t()
style_base.init()
style_base.set_bg_color(lv.palette_main(lv.PALETTE.LIGHT_GREEN))
style_base.set_border_color(lv.palette_darken(lv.PALETTE.LIGHT_GREEN, 3))
style_base.set_border_width(2)
style_base.set_radius(10)
style_base.set_shadow_width(10)
style_base.set_shadow_ofs_y(5)
style_base.set_shadow_opa(lv.OPA._50)
style_base.set_text_color(lv.color_black())
style_base.set_width(200)
style_base.set_height(50)
style_base.set_height(lv.SIZE_CONTENT)

# Create an object with the base style only
obj_base = lv.obj(lv.scr_act())
obj_base.add_style(style_base, 0)
obj_base.align(lv.ALIGN.LEFT_MID, 60, 0)

label = lv.label(obj_base)
label.set_text('Hello World')
label.center()
