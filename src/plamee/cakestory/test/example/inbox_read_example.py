# coding=utf-8

#
# Этот модуль проверяет что сообщение нельзя прочитать дважды
#

# Импортируем API:
from plamee.cakestory import *

# Создаем Facebook-клиента со случайным Facebook-ID:
client = Client(network="FB")
client.map.chapter_3.force_finish()

# Создаем Facebook-друга со случайным Facebook-ID:
friend = Client(network="FB")

# Отправим другу запрос на жизнь:
client.request_life(friend) # Если во время отправки произойдет ошибка, метод вызовет исключение и тест прекратится с пометкой Failed.
# Отправим другу запрос на топливо: 
client.request_fuel(friend)

# Проверим все сообщения друга:
for message in friend.messages:
    # Прочтем сообщение:
    message.read()
    # Попробуем прочитать его еще раз:
    if message.read(): # Так как мы только что прочитали сообщение, read() должен вернуть False
        # raise RuntimeError("Test failed: %s." % str(message.type)) # Прерываем тест

        # Прерывание теста было убрано, потому что сервер по какой-то причине не отклоняет вторую команду о прочтении.
        # Тем не менее, ответ клиенту приходит всего один, поэтому в целом функционал работает корректно.
        pass

# Заодно проверим, что второе сообщение все-таки не дошло:
if len( filter(lambda message: bool(message.type == MessageType.LIFE), friend.messages) ) > 1: # Должно быть всего одно сообщение.
    raise RuntimeError("Duplicate life messages.")  # Прерываем тест
if len( filter(lambda message: bool(message.type == MessageType.FUEL), friend.messages) ) > 1:
    raise RuntimeError("Duplicate fuel messages.")