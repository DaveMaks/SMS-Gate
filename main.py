from datetime import datetime, timedelta
import re

import serial
import time

from log import Log
from server import API
from sms_gate import SmsGate
from transliterate import get_available_language_codes
from transliterate import translit


def IsReady(gate):
    count_connect = state_module = state = 0

    # Проверка на иницмализацию Модуля
    state_module = int(gate.GetStatus() or 0)
    while state_module != 1 and count_connect < 3:
        time.sleep(1)
        count_connect += 1
        state_module = int(
            gate.GetStatus() or 0)
    if state_module != 1:
        Log.Warning('Module: ' + SmsGate.STATUS_MODULE[state_module])
        gate.Stop(True)
        return False
    else:
        Log.Debug('Module: ' + SmsGate.STATUS_MODULE[state_module])

    # Проверка на иницмализацию сети
    count_connect = 0
    state = int(gate.GetRegistr() or 0)
    while state != 1 and count_connect < 3:
        time.sleep(1)
        count_connect += 1
        state = int(gate.GetRegistr() or 0)

    if state != 1:
        Log.Warning('Error Connect ' + SmsGate.STATUS_REGISTR[state])
        gate.Stop(True)
        return False
    else:
        Log.Debug('Connect: ' + SmsGate.STATUS_REGISTR[state])
    # time.sleep(1)
    return gate.command('AT')


def ConfigModem(gate):
    if not gate.setSMSType(1):
        return False
    if not gate.setSMSCharset("GSM"):
        return False
    return True


def FinalMessage(ref_srv: API, msg):
    count_test = 0
    msg_del = False
    while not msg_del or count_test < 10:
        msg_del = ref_srv.DeleteMessages(msg['id'])
        if msg_del:
            return True
        count_test += 1
        Log.Warning("Non-emissions of harmful substances: %s" % (msg))
        time.sleep(2)
    return False


serialPort = serial.Serial(
    port='/dev/ttyS1',
    baudrate=115200,
    bytesize=8, timeout=2,
    stopbits=serial.STOPBITS_ONE
)

srv = API("https://sms.url.kz")
while True:
    msgList = srv.GetMessages()
    if not msgList or not len(msgList) > 0:
        time.sleep(2)
        continue

    with SmsGate(connect=serialPort) as gate:
        gate.Run()
        if not IsReady(gate):
            time.sleep(1)
            continue
        if not ConfigModem(gate):
            time.sleep(1)
            continue

        for msg in msgList:
            try:
                if not msg['id'] or msg['id'] == "":
                    Log.Warning("Error ID: %s" % (msg))

                if not re.match(r'77\d{9}', msg['phones']):
                    raise Exception("Error phone: %s" % (msg))

                if not msg['message'] or msg['message'] == "":
                    raise Exception("Error messages: %s" % (msg))

                msg['message'] = translit(msg['message'], language_code='ru', reversed=True)
                if not re.match(r'^.{3,159}$', msg['message']):
                    raise Exception("Error messages: %s" % (msg))

                msg['date'] = datetime.strptime(msg['date'], '%d-%m-%Y %H:%M:%S')
                if msg['date'] < (datetime.now() - timedelta(minutes=5)):
                    raise Exception("TimeOut messages: %s" % (msg))

                Log.Info("Get Message: %s" % (msg))
                if not gate.SendMessage('+' + msg['phones'], msg['message']):
                    raise Exception('Сообщение не отправленно')

                if FinalMessage(srv, msg):
                    Log.Info("Сompleted: %s" % (msg))
                else:
                    raise Exception("Job could not be deleted: %s" % (msg))
                continue

            except Exception as e:
                Log.Warning(e)
                if FinalMessage(srv, msg):
                    Log.Info("Сompleted: %s" % (msg))

        gate.Stop(True)
exit(0)