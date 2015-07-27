# coding=utf-8

#
# Этот модуль проверяет, что сервер зачисляет верное количество бустеров при покупке
#

# Импортируем API:
from plamee.cakestory import *

# Создаем Facebook-клиента, так как сторейдж работает только для социальных сетей
client = Client(network="FB")

# Проходим по всем бустерам:
for booster in client.boosters:
    # Не все бустеры можно купить, например, +3 хода
    # Поэтому пропускаем те, которые купить нельзя, иначе сервер вернет ошибку
    if not booster.for_buy:
        continue

    # Изменяем текущий прогресс клиента,
    # если он недостаточный, чтобы купить бустер
    if client.progress < booster.level:
        client.map.get_level(booster.level).force_finish()

    # Сохраняем текущее количество бустеров
    count = booster.count
    # Делаем покупку
    if not booster.force_buy(1):
        raise RuntimeError("Cannot buy booster.")

    # Проверяем, что количество изменилось верно
    if count + booster.pack_count != booster.count:
        raise RuntimeError("Booster count test failed.")
