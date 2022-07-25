# SMS-Gate
Служба для рассылки СМС сообщений через модуль M590E

### Основные AT комманды
[Описание и команды управления](https://radiolaba.ru/microcotrollers/gsm-modul-neoway-m590-opisanie-i-komandyi-upravleniya.html "Описание и команды управления")

[Hardware User Guide](http://wless.ru/files/GSM/Neoway/Neoway_M590E_V1_GSM_Module_Hardware_User_Guide_V1_0.pdf "Hardware User Guide")


### Установка дополнительных библиотек
```bash
python3 -m venv env
pip3 install pyserial
pip install -U transliterate
```

### Добавить как службу
```bash
cp ./sms_gate /etc/init.d/sms_gate
update-rc.d sms_gate defaults
```
