#!/usr/bin/env python3
# -*-coding: utf-8-*-
import queue
import sys
import time
import traceback
from threading import Thread
import re

import serial
from queue import Queue

from log import Log


class SmsGate:
    TERMINATOR = b'\r\n'

    __connect = None
    responses = None
    __readThread = None
    isReadPort = False
    __count = 0
    lock = None

    STATUS_REGISTR = [
        'не зарегистрирован, поиск сети не выполняется',
        'зарегистрирован в домашней сети',
        'регистрация отклонена',
        'не зарегистрирован выполняется поиск сети',
        'неизвестно',
        'зарегистрирован, зона роуминга'
    ]

    STATUS_MODULE = [
        'N/D-0',
        'готов к работе',
        'N/D',
        'неизвестно',
        'входящий звонок',
        'в режиме соединения',
        'спящий режим',
    ]

    def __init__(self, connect: serial.Serial):
        self.__connect = connect
        self.responses = Queue()

    def Run(self):
        if not self.__connect.is_open:
            self.__connect.open()
        if not self.__readThread:
            self.__readThread = Thread(target=self.thread_function, args=(1,))
        if not self.isReadPort:
            self.__readThread.start()
        self.write(bytes.fromhex('1A'))
        self.command('ATE0')

    def Stop(self, isWait=False):
        self.isReadPort = False
        if isWait:
            self.Wait();

    def Wait(self):
        if self.__readThread:
            self.__readThread.join()

    def thread_function(self, param):
        self.isReadPort = True
        Log.Info('Start Read serialPort')
        while self.isReadPort and self.__connect.is_open:
            try:
                # read all that is there or wait for one byte (blocking)
                data = self.__connect.read(self.__connect.in_waiting or 1).decode("utf-8").split(
                    self.TERMINATOR.decode())
                lines = list(filter(lambda s: s != "", list(map(lambda x: x.strip(), data))))
            except serial.SerialException as e:
                Log.Warning(str(e))
                break
            else:
                if lines:
                    try:
                        list(map(self.responses.put, lines))
                        # self.responses.put(lines, timeout=2)
                    except Exception as e:
                        Log.Warning(str(e))
                        break
        Log.Info('Stop Read serialPort')
        self.isReadPort = False

    def write(self, data):
        if self.__connect.is_open:
            return self.__connect.write(data)

    def close(self):
        self.__connect.close()
        self.Stop()

    def command(self, command: str, response='OK', timeout=3):
        if type(command) is str:
            self.write(command.encode('utf-8') + self.TERMINATOR)
        if type(command) is bytes:
            self.write(command)
        lines = []
        # time.sleep(0.5)
        while True:
            line = ''
            try:
                line = self.responses.get(timeout=timeout)
                lines.append(line)
                if line == response:
                    Log.Info('%s -> %r' % (command, lines))
                    return lines
            except queue.Empty:
                Log.Debug(
                    'Request none command={0}, response={1}, lines={2}  line={3}'.format(command, response, lines,
                                                                                         line))
                break

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    # Команда проверки статуса модуля
    def GetStatus(self):
        ret = self.command(command="AT+CPAS")
        if not ret or not ret.__len__() > 0:
            return None
        result = re.findall(r'\+CPAS: (\d)', ret[0])
        if len(result) != 1:
            return None
        return int(result[0]) + 1

    # Команда проверки регистрации модуля в сети
    def GetRegistr(self):
        ret = self.command(command="AT+CREG?")
        if (not ret) or not ret.__len__() > 0:
            return None
        result = re.findall(r'\+CREG: (\d),(\d)', ret[0])
        if not len(result) > 0:
            return None
        if len(result[0]) != 2:
            return None
        return int(result[0][1])

    # Команда настройки формата SMS сообщений
    # 0 – PDU формат; 1 – текстовый формат
    def setSMSType(self, type_sms=1):
        ret = self.command('AT+CMGF=' + str(type_sms))
        return ret is not None

    # выбора кодировки текста
    # “GSM” – кодировка ASCII
    # “HEX” – кодировка шестнадцатеричными значениями
    # “IRA” – международный справочный алфавит
    # “PCCP437” – кодировка CP437 (IBM PC)
    # “8859-1” – кодовые страницы семейства ISO 8859
    # “UCS2” – кодировка Unicode (2 байта на символ)
    def setSMSCharset(self, charset="GSM"):
        ret = self.command('AT+CSCS="' + str(charset) + '"')
        return ret is not None

    def SendMessage(self, phone: str, message: str):
        # TODO проверка формата номера и переведение в формату +77ххх.ххх
        ret = self.command('AT+CMGS="' + phone + '"', response='>', timeout=2)
        if not ret:
            Log.Warning("Error Send SMS")
            return False
        ret = self.command(message.encode('utf-8') + bytes.fromhex('1A'), timeout=5)
        if ret:
            Log.Info("Message Send to %s: %s" % (phone, message))
            return True
        return False

        def Call(self, phone: str):
            self.command('ATD+' + phone)
            while True:
                if not self.responses.empty():
                    print(self.responses.get());
