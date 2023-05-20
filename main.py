import dht
import time
import network
import machine
import ujson
from umqttsimple import MQTTClient
from machine import Pin, ADC

l_state = 0
fire = 0

# 初始化
def init():
    global d, Pin38, Pin39, Pin40 ,Pin41 ,Pin42 ,Pin21 ,Pin14, Pin9, Pin13
    Pin38 = Pin(38, Pin.IN)
    d = dht.DHT11(Pin38)
    Pin9 = Pin(9, Pin.IN) #火焰传感器
    Pin14 = Pin(14, Pin.OUT) #蜂鸣器
    Pin42 = Pin(42, Pin.OUT) #补光灯
    Pin41 = Pin(41, Pin.OUT) #温度提示灯
    Pin40 = Pin(40, Pin.OUT)
    Pin39 = Pin(39, Pin.OUT)
    Pin21 = Pin(21, Pin.OUT) #水泵
    Pin13 = Pin(13, Pin.IN) #光传感器
    Pin39.off()
    Pin40.off()
    Pin41.off()
    Pin42.off()
    Pin21.off()

#温湿度处理
def temp_hum():
    global temp,hum
    d.measure()
    temp = d.temperature()
    hum = d.humidity()
    if temp <= 26:
        Pin39.on()
        Pin40.off()
        Pin41.off()
    if temp >= 28:
        Pin39.off()
        Pin40.on()
        Pin41.off()
    if temp == 27:
        Pin39.off()
        Pin40.off()
        Pin41.on()

#火焰报警
def flame():
    global fire
    Pin14.value(not Pin9.value())
    a = Pin9.value()
    if (a == 1):
        fire = 1
    else:
        fire = 0
        
#光照
def lighting():
    global light
    global l_state
    adc = ADC(Pin13)
    light = adc.read()
    if (light <= 1000):
        Pin42.on()
    if (light > 1000) and (l_state == 0):
        Pin42.off()
    if (light > 1000) and (l_state == 1):
        Pin42.on()
        

def watering():
    if hum < 60:
        Pin21.value(1)
        time.sleep(10)
        Pin21.value(0)

#连接网络
def do_connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect('Shelby', '888888888')
        i = 1
        while not wlan.isconnected():
            print("正在连接...{}".format(i))
            i += 1
            time.sleep(1)
    print('network config:', wlan.ifconfig())
    

#设置回调函数
def sub_cb(topic, msg): # 回调函数，收到服务器消息后会调用这个函数
    global topic1 
    global msg1
    global l_state
    topic1 = topic.decode("utf-8")
    msg1 = msg.decode("uft-8")
    print(topic1, msg1)
    if topic1 == "led" and msg1 == "On":
        Pin42.value(1)
        l_state = 1
    elif topic1 == "led" and msg1 == "Off":
        Pin42.value(0)
        l_state = 0
    elif topic1 == "watering" and msg1 == "On":
        Pin21.value(1)
    elif topic1 == "watering" and msg1 == "Off":
        Pin21.value(0)  

#建立MQTT通信
def set_MQTT():
    global c
    topics = [b"watering", b"led"]
    c = MQTTClient("ESP32-S3-BOX-Lite", "192.168.195.1")
    c.connect()  # 建立连接
    c.set_callback(sub_cb)
    for topic in topics:
        c.subscribe(topic)  # 监控通道，接收控制命令


def send_msg():
    mqtt_topic1 = "Temp"
    mqtt_topic2 = "Hum"
    mqtt_topic3 = "Fire"
    mqtt_topic4 = "Light"
    data1 = {"temperature": temp}
    data2 = {"humidity": hum}
    data3 = {"fire": fire}
    data4 = {"Light": light}
    data1_json = ujson.dumps(data1)
    data2_json = ujson.dumps(data2)
    data3_json = ujson.dumps(data3)
    data4_json = ujson.dumps(data4)
    c.publish(mqtt_topic1, data1_json)
    c.publish(mqtt_topic2, data2_json)
    c.publish(mqtt_topic3, data3_json)
    c.publish(mqtt_topic4, data4_json)
    

def loop():
    while True:
        c.check_msg()
        time.sleep_ms(200)
        temp_hum()
        flame()
        lighting()
        watering()
        send_msg()
        time.sleep_ms(200)
    

if __name__ == '__main__':
    init()
    do_connect()
    set_MQTT()
    loop()
    