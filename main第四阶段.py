


import urequests
import network
import socket
import time
import json
from machine import Pin,Timer,ADC

DEVICE_ID='698146184'                                              #设备ID
API_KEY='w24XDwnqukFiV0YUXdpIEpJLqZY='                             #API_KEY

SSID="WWR"                                                         #WIFI名称
PASSWORD="11211037"                                                #WIFI密码
wlan=None
s=None

TEST = True                                                        #TTL检测传送标志测试

data_name_list = ["Volume_flag","Volume_scale","$OneNET_LBS_WIFI","Time","OneNET_LBS_WIFI"]#上传数据流名称列表
data_list = [0,0,{},"0.0.0.0",{}]                                  #上传数据列表

led = Pin(2,Pin.OUT)                                               #板载LED初始化
TTL = Pin(39,Pin.IN)                                               #TTL输入初始化
Adc = ADC(Pin(36))                                                  #Analog输入初始化
KEY = Pin(0,Pin.IN)                                                #板载按键初始化

B_time = Timer(1)                                                  #定时器初始化
Send_time = Timer(2)

led.value(1)                                                       #led灯初始化

#def blink(t):
 # led.value(not led.value())
def Indicator(bool):                                              #蓝色板载led作为指示灯，当上传数据时亮起  
    led.value(bool)
 
def TTL_detction():                                                #TTL输入检测函数
   temp = TTL.value()
   return temp
def KEY_detction():                                                #板载按键检测
    key = KEY.value()
    while(key==0):
      if(KEY.value()==1):
        global TEST
        TEST = True
        break

def WIFI_location():                                               #附近Wifi mac地址扫描处理
   wifi_info = wlan.scan()
   #print(wifi_info)
   s = wifi_info[1][1]
   MAC1 = ("%02x:%02x:%02x:%02x:%02x:%02x") %(s[0],s[1],s[2],s[3],s[4],s[5])
   #print(MAC1)
   RSSI1 = "%d"%(wifi_info[1][3])
   s = wifi_info[2][1]
   MAC2 = ("%02x:%02x:%02x:%02x:%02x:%02x") %(s[0],s[1],s[2],s[3],s[4],s[5])
   RSSI2 = "%d"%(wifi_info[2][3])
   wifi_lbs_data = {"macs":MAC1+","+RSSI1+"|"+MAC2+","+RSSI2}
   #print (wifi_lbs_data)
   return wifi_lbs_data
 
def Auto_Send(t1):                                                #定时器自动发送
   #Send_data(data_name_list,data_list)
   #global TEST
   #TEST = True
   print(t1)
  
def Send_data(data_name_list,data_list):                           #发送将列表中数据进行处理传递，保证两个list长度相同
  for i in range(len(data_name_list)):
    res = http_put_data(data_name_list[i],data_list[i])
    print(res.json())
    

def connectWifi(ssid,passwd):                                      #WIFI连接函数
  global wlan
  wlan=network.WLAN(network.STA_IF)
  wlan.active(True)
  wlan.disconnect()
  wlan.connect(ssid,passwd)
  while(wlan.ifconfig()[0]=='0.0.0.0'):
    time.sleep(1)
  return True
  
  
def http_get_data():                                               #利用GET从服务器获取定位数据
    url_Get='http://api.heclouds.com/devices/'+DEVICE_ID+'/lbs/latestWifiLocation'
    r = urequests.get(url_Get,headers={"api-key":API_KEY})  
    parsed = r.json()
    #print(parsed)
    Time = parsed["data"]["at"]
    data_list[3] = Time[5:19]
    #print (data_list[3])
    
    LON = parsed["data"]["lon"]
    LAT = parsed["data"]["lat"]
    location_infor={"lon":LON,"lat":LAT}
    data_list[4] = location_infor
    #print(LON)
    #print(LAT)
    #print(data_list[3])

    
def http_put_data(data_name,data):                                  #将处理好的数据进行POST发送
  
    url_Post='http://api.heclouds.com/devices/'+DEVICE_ID+'/datapoints'
    values={'datastreams':[{"id":data_name,"datapoints":[{"value":data}]}]}
    jdata = json.dumps(values)                 
    r=urequests.post(url_Post,data=jdata,headers={"api-key":API_KEY})
    return r
try:
  connectWifi(SSID,PASSWORD)                                        #连接WIFI
 
  data_list[2]=WIFI_location()                                      #扫描周围WIFI
  #B_time.init(period=4000,mode=Timer.PERIODIC,callback=blink)
  Send_time.init(period=10000,mode=Timer.PERIODIC,callback=Auto_Send)#定时器初始化
  Indicator(0)
  while True:                                                        #循环执行
    TTL_Signal = TTL_detction()
    KEY_detction()
    #if(TTL_Signal ==1 or TEST == True):
    if(TEST == True):
    #if(KEY_detction()):

      Indicator(1)
      data_list[0] = KEY.value()
      #data_list[0] = TTL_Signal
      data_list[1] = Adc.read()
      
      
      http_get_data()
      Send_data(data_name_list,data_list)
    
      TEST = False
      Indicator(0)
    else:
      Indicator(0)
   
   
   
except:
  wlan.disconnect()
  wlan.active(False)
  #B_time.deinit()








