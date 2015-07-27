# coding=utf-8

#
# Этот модуль проверяет, что нельзя завершить уровень в закрытом чаптере
#

# Импортируем API:
from plamee.cakestory import *

# Создаем случайного клиента:
client = Client()

map = client.map
chapter = map.current_chapter

# Проходим по всем чаптерам, кроме последнего:
while chapter.next is not None:
    # Проходим все уровни в чаптере:
    if not chapter.force_finish():
        raise RuntimeError("Cannot finish chapter.")

    # Пробуем пройти уровень в следующем чаптере, пока он закрыт:
    if map.current_level.finish():
        raise RuntimeError("Test failed.")

    # Переходим к следующему чаптеру:
    chapter = chapter.next