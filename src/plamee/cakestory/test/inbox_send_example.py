# coding=utf-8

#
# Этот модуль проверяет, что сообщения "life" и "booster" не отправляются дважды.
#

# Импортируем API:
from plamee.cakestory import *

# Создаем Facebook-клиента со случайным Facebook-ID:
client = Client(network="FB")
# Создаем Facebook-друга со случайным Facebook-ID:
friend = Client(network="FB")

# Отправим другу жизнь:
client.send_life(friend) # Если во время отправки произойдет ошибка, метод вызовет исключение и тест прекратится с пометкой Failed.
# Отправим другу бустер "+3 хода" 
client.send_help(friend) 

# Попробуем отправить другу жизнь еще раз и проверим результат:
if client.send_life(friend): # Так как мы только что послали жизнь, send_life() должен вернуть False
    raise RuntimeError("Test failed: send_life.") # Прерываем тест
if client.send_help(friend):
    raise RuntimeError("Test failed: send_help.")

# Заодно проверим, что второе сообщение все-таки не дошло:
if len( filter(lambda message: bool(message.type == MessageType.LIFE), friend.messages) ) > 1: # Должно быть всего одно сообщение.
    raise RuntimeError("Test failed.")  # Прерываем тест
if len( filter(lambda message: bool(message.type == MessageType.HELP), friend.messages) ) > 1:
    raise RuntimeError("Test failed.")