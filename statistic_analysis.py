import sqlite3

def send_statistic():

    try:
        sqlite_connection = sqlite3.connect('alg_dir/data.db')
        sqlite_connection_quest = sqlite3.connect('quest_dir/data_quest.db')
        cursor = sqlite_connection.cursor()
        cursor_quest = sqlite_connection_quest.cursor()
        print("Подключен к SQLite")

        ## С учетом той базы, что я вел до этого

        sqlite_select_query = """SELECT * from summ where userid != 798637297;"""
        cursor.execute(sqlite_select_query)
        records = cursor.fetchall()
        all_str = len(records)

        sqlite_select_query = """SELECT DISTINCT userid from summ;"""
        cursor.execute(sqlite_select_query)
        records = cursor.fetchall()
        uniq_str = len(records)

        sqlite_select_query = """SELECT * from stat where startDS = 'ДС' AND userid != 798637297;"""
        cursor.execute(sqlite_select_query)
        records = cursor.fetchall()
        all_DS = len(records)

        sqlite_select_query = """SELECT * from stat where startDS = 'ЕдП' AND userid != 798637297;"""
        cursor.execute(sqlite_select_query)
        records = cursor.fetchall()
        all_EdP = len(records)

        sqlite_select_query = """SELECT * from stat where startDS = 'МСЗ' AND userid != 798637297;"""
        cursor.execute(sqlite_select_query)
        records = cursor.fetchall()
        all_MSZ = len(records)

        sqlite_select_query = """SELECT * from quest where userid != 798637297;"""
        cursor_quest.execute(sqlite_select_query)
        records = cursor_quest.fetchall()
        all_quest = len(records)


        sqlite_select_query = """SELECT * from summ where datetime between date('now', '-31 day', '+3 hour') AND date('now' , '+4 hour') AND userid != 798637297;"""
        cursor.execute(sqlite_select_query)
        records = cursor.fetchall()
        month_str = len(records)

        sqlite_select_query = """SELECT * from stat where startDS = 'ДС'  AND userid != 798637297 AND datetime between date('now', '-31 day') AND date('now', '+4 hour');"""
        cursor.execute(sqlite_select_query)
        records = cursor.fetchall()
        month_DS = len(records)

        sqlite_select_query = """SELECT * from stat where startDS = 'ЕдП'  AND userid != 798637297 AND datetime between date('now', '-31 day') AND date('now', '+4 hour');"""
        cursor.execute(sqlite_select_query)
        records = cursor.fetchall()
        month_EdP = len(records)

        sqlite_select_query = """SELECT * from stat where startDS = 'МСЗ'  AND userid != 798637297 AND datetime between date('now', '-31 day') AND date('now', '+4 hour');"""
        cursor.execute(sqlite_select_query)
        records = cursor.fetchall()
        month_MSZ = len(records)

        sqlite_select_query = """SELECT * from quest where userid != 798637297 AND datetime between date('now', '-31 day') AND date('now', '+4 hour');"""
        cursor_quest.execute(sqlite_select_query)
        records = cursor_quest.fetchall()
        month_quest = len(records)



        sqlite_select_query = """SELECT * from summ where datetime between date('now', '-7 day', '+3 hour') AND date('now' , '+4 hour') AND userid != 798637297;"""
        cursor.execute(sqlite_select_query)
        records = cursor.fetchall()
        week_str = len(records)

        sqlite_select_query = """SELECT * from stat where startDS = 'ДС'  AND userid != 798637297 AND datetime between date('now', '-7 day') AND date('now', '+4 hour');"""
        cursor.execute(sqlite_select_query)
        records = cursor.fetchall()
        week_DS = len(records)

        sqlite_select_query = """SELECT * from stat where startDS = 'ЕдП'  AND userid != 798637297 AND datetime between date('now', '-7 day') AND date('now', '+4 hour');"""
        cursor.execute(sqlite_select_query)
        records = cursor.fetchall()
        week_EdP = len(records)

        sqlite_select_query = """SELECT * from stat where startDS = 'МСЗ'  AND userid != 798637297 AND datetime between date('now', '-7 day') AND date('now', '+4 hour');"""
        cursor.execute(sqlite_select_query)
        records = cursor.fetchall()
        week_MSZ = len(records)

        sqlite_select_query = """SELECT * from quest where userid != 798637297 AND datetime between date('now', '-7 day') AND date('now', '+4 hour');"""
        cursor_quest.execute(sqlite_select_query)
        records = cursor_quest.fetchall()
        week_quest = len(records)

        sqlite_select_query = """SELECT val from grade where val=CAST(val AS INTEGER) AND userid != 798637297;"""
        cursor.execute(sqlite_select_query)
        records = cursor.fetchall()
        gr = []
        past_grad = [1,3,3,3,3,2,3,3,3,3,3]
        gr.extend(past_grad)
        for i in records:
            gr.append(int(i[0]))
        if not len(gr) == 0:
            num_grad = len(gr)
            mean_grad = round(10 * (sum(gr) / len(gr)) / 3, 2)


        cursor.close()
        cursor_quest.close()

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if sqlite_connection:
            sqlite_connection.close()
            print("Соединение с SQLite закрыто")

    text = "*Общая статистика*" \
           "\n├  Количество пользователей  - " + str(all_str) + \
           "\n├  Уникальных пользователей - " + str(uniq_str) + \
           "\n├  Прохождений ДС - " + str(all_DS) + \
           "\n├  Прохождений МСЗ - " + str(all_MSZ) + \
           "\n├  Прохождений ЕдП - " + str(all_EdP) + \
           "\n├  Задали вопросы - " + str(all_quest) + \
           "\n├  Количество оценок - " + str(num_grad) + \
           "\n└ Средняя оценка - " + str(mean_grad) + \
           "\n" \
           "\n*Статистика за месяц*" \
           "\n├  Количество пользователей  - " + str(month_str) + \
           "\n├  Прохождений ДС - " + str(month_DS) + \
           "\n├  Прохождений МСЗ - " + str(month_MSZ) + \
           "\n├  Прохождений ЕдП - " + str(month_EdP) + \
           "\n└  Задали вопросы - " + str(month_quest) + \
           "\n" \
           "\n*Статистика за неделю*" \
           "\n├  Общее количество  - " + str(week_str) + \
           "\n├  Общее число ДС - " + str(week_DS) + \
           "\n├  Общее число МСЗ - " + str(week_MSZ) + \
           "\n├  Общее число ЕдП - " + str(week_EdP) + \
           "\n└  Задали вопросы - " + str(week_quest)
    return text