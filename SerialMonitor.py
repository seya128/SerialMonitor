# PySimpleGUIを使ったシリアルモニター
# ArduinoIDEのシリアルモニターとほとんど同じです

import PySimpleGUI as sg
import datetime
import serial
from serial.tools import list_ports


# 改行コード
DICT_NEWLINE = {
  'none':   '', 
  'LF':     '\n',
  'CR':     '\r',
  'CR+LF':  '\r\n'
}

# ボーレート
LIST_BAUDRATE = [
  '300 bps',
  '1200 bps',
  '2400 bps',
  '4800 bps',
  '9600 bps',
  '19200 bps',
  '38400 bps',
  '57600 bps',
  '74880 bps',
  '115200 bps',
  '230400 bps',
  '250000 bps',
  '500000 bps',
  '1000000 bps',
  '2000000 bps'
]

# COMポートリスト
def list_port():

  ports = list_ports.comports()    # ポートデータを取得
  
  devices = [info.device for info in ports]
  
  return devices

# COMポートオープン
def open_port(port, baudrate):
  ser = serial.Serial()
  ser.baudrate = int(baudrate[0:-4])
  ser.timeout = 0.01       # タイムアウトの時間(秒)
  ser.port = port
  # 開いてみる
  try:
      ser.open()
      return ser
  except:
      print("error when opening serial")
      return None


# 出力エリアにプリント
def printOut(s, sep, scroll, timestamp):
    if timestamp==True:
      now = datetime.datetime.now().strftime('%H:%M:%S.%f')
      sg.cprint(now[0:-3]+sep+s,end="", autoscroll=scroll)
    else:
      sg.cprint(s,end="", autoscroll=scroll)



# シリアルモニター

com_list = list_port()

layout = [
   [
     sg.Input('', size=(10,1), font=('ＭＳ ゴシック',10),  expand_x=True, key='-IN-'), 
     sg.Button('Send', bind_return_key=True, key='-SEND-')
   ],
   [sg.Multiline('', size=(80,30), font=('ＭＳ ゴシック',10), expand_x=True, expand_y=True, key='-OUT-')],
   [
     sg.Checkbox('AutoScroll', default = True, key='-AutoScroll-'), 
     sg.Checkbox('Timestamp', default = False, key='-Timestamp-'),
     sg.Stretch(),
     sg.Combo(values=list(DICT_NEWLINE.keys()), default_value='LF', readonly=True, key='-newline-'),
     sg.Combo(values=com_list, default_value=com_list[0], enable_events=True, readonly=True, key='-port-'),
     sg.Combo(values=LIST_BAUDRATE, default_value='115200 bps',  enable_events=True, readonly=True, key='-baudrate-'),
     sg.Button('Clear', key='-CLEAR-')
   ]
]

window = sg.Window('Serial Monitor', layout, resizable=True,return_keyboard_events=True)

sg.cprint_set_output_destination(window, '-OUT-');


ser = open_port(window['-port-'].DefaultValue, window['-baudrate-'].DefaultValue)

while True:             # Event Loop
  event, values = window.read(timeout = 2)  # timeoutの単位はms
  if event == sg.WIN_CLOSED:
    break
  if event == '-SEND-':
    w_data = values['-IN-']+DICT_NEWLINE[values['-newline-']]
    try:
      ser.write(w_data.encode())
    finally:
      #printOut(values['-IN-']+'\n', ' <- ', values['-AutoScroll-'], values['-Timestamp-'])
      window['-IN-'].update('');
  if event == '-port-' or event == '-baudrate-':
    if ser is not None:
      ser.close();
    ser = open_port(values['-port-'], values['-baudrate-'])
  if event == '-CLEAR-':
    window['-OUT-'].update('')
  
  if ser is not None:
    if ser.is_open:
      while (True):
        data = ser.readline()
        if data == b'':
          break
        try:
          printOut(data.decode(), ' -> ', values['-AutoScroll-'], values['-Timestamp-']) 
        except:
          print('Decode Error')

if ser is not None:
  ser.close()
  
window.close()

