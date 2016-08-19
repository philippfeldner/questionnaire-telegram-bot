import pickle
import sqlite3
import time
from admin import settings


class Participant:
    chat_id_ = 0
    language_ = ''
    gender_ = ''
    country_ = ''
    day_ = 0
    block_ = -1
    question_ = -1
    pointer_ = 0
    time_t_ = ''
    time_offset_ = 0xFFFF
    conditions_ = []
    next_block = None

    job = None
    q_set_ = None
    auto_queue_ = False
    block_complete_ = False
    q_idle_ = False
    active_ = True
    last_ = False

    def __init__(self, chat_id=None, init=True):
        self.chat_id_ = chat_id
        if init:
            try:
                db = sqlite3.connect('survey/participants.db')
                db.execute("INSERT INTO participants (ID, conditions, time_t,"
                           "country, gender, language, question, day, block, time_offset, q_idle, active, pointer)"
                           "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                           (chat_id, pickle.dumps([]), '', '', '', '', -1, 1, -1, 0xFFFF, 0, 1, 0))
                db.commit()
                db.close()
                text = "User:\t" + str(self.chat_id_) + "\tregistered.\t" + time.strftime("%X %x\n")
                try:
                    with open('log.txt', 'a') as log:
                        log.write(text)
                except OSError or IOError as error:
                    print(error)
            except sqlite3.Error as error:
                print(error)

    def set_language(self, language):
        if language == ('Deutsch' or 'de'):
            lang = 'de'
        elif language == ('English' or 'en'):
            lang = 'en'
        elif language == ('Español' or 'es'):
            lang = 'es'
        elif language == ('Français' or 'fr'):
            lang = 'fr'
        else:
            lang = settings.default_language

        self.language_ = lang
        try:
            db = sqlite3.connect('survey/participants.db')
            db.execute("UPDATE participants SET language=? WHERE ID=?", (lang, self.chat_id_))
            db.commit()
            db.close()
        except sqlite3.Error as error:
            print(error)
        return

    def set_gender(self, gender):
        self.gender_ = gender
        try:
            db = sqlite3.connect('survey/participants.db')
            db.execute("UPDATE participants SET gender=? WHERE ID=?", (gender, self.chat_id_))
            db.commit()
            db.close()
        except sqlite3.Error as error:
            print(error)
        return

    def set_country(self, country):
        self.country_ = country
        try:
            db = sqlite3.connect('survey/participants.db')
            db.execute("UPDATE participants SET country=? WHERE ID=?", (country, self.chat_id_))
            db.commit()
            db.close()
        except sqlite3.Error as error:
            print(error)
        return

    def set_day(self, day):
        self.day_ = day
        try:
            db = sqlite3.connect('survey/participants.db')
            db.execute("UPDATE participants SET day=? WHERE ID=?", (self.day_, self.chat_id_))
            db.commit()
            db.close()
        except sqlite3.Error as error:
            print(error)
        return self.day_

    def set_time_t(self, time_t):
        self.time_t_ = time
        try:
            db = sqlite3.connect('survey/participants.db')
            db.execute("UPDATE participants SET time_t=? WHERE ID=?", (time_t, self.chat_id_))
            db.commit()
            db.close()
        except sqlite3.Error as error:
            print(error)
        return

    def set_time_offset(self, offset):
        self.time_offset_ = offset
        try:
            db = sqlite3.connect('survey/participants.db')
            db.execute("UPDATE participants SET time_offset=? WHERE ID=?", (offset, self.chat_id_))
            db.commit()
            db.close()
        except sqlite3.Error as error:
            print(error)
        return

    def add_conditions(self, conditions):
        if conditions == []:
            return
        self.conditions_ += conditions
        try:
            db = sqlite3.connect('survey/participants.db')
            cond = pickle.dumps(self.conditions_)
            db.execute("UPDATE participants SET conditions=? WHERE ID=?", (cond, self.chat_id_))
            db.commit()
            db.close()
        except sqlite3.Error as error:
            print(error)
        return

    def set_block(self, block):
        self.block_ = block
        try:
            db = sqlite3.connect('survey/participants.db')
            db.execute("UPDATE participants SET block=? WHERE ID=?", (self.block_, self.chat_id_))
            db.commit()
            db.close()
        except sqlite3.Error as error:
            print(error)
        return self.block_

    def increase_block(self):
        self.block_ += 1
        try:
            db = sqlite3.connect('survey/participants.db')
            db.execute("UPDATE participants SET block=? WHERE ID=?", (self.block_, self.chat_id_))
            db.commit()
            db.close()
        except sqlite3.Error as error:
            print(error)
        return self.block_

    def set_question(self, question):
        self.question_ = question
        try:
            db = sqlite3.connect('survey/participants.db')
            db.execute("UPDATE participants SET question=? WHERE ID=?", (self.question_, self.chat_id_))
            db.commit()
            db.close()
        except sqlite3.Error as error:
            print(error)
        return self.question_

    def increase_question(self):
        self.question_ += 1
        try:
            db = sqlite3.connect('survey/participants.db')
            db.execute("UPDATE participants SET question=? WHERE ID=?", (self.question_, self.chat_id_))
            db.commit()
            db.close()
        except sqlite3.Error as error:
            print(error)
        return self.question_

    def set_pointer(self, pointer):
        self.pointer_ = pointer
        try:
            db = sqlite3.connect('survey/participants.db')
            db.execute("UPDATE participants SET pointer=? WHERE ID=?", (self.pointer_, self.chat_id_))
            db.commit()
            db.close()
        except sqlite3.Error as error:
            print(error)
        return self.pointer_

    def increase_pointer(self):
        self.pointer_ += 1
        try:
            db = sqlite3.connect('survey/participants.db')
            db.execute("UPDATE participants SET pointer=? WHERE ID=?", (self.pointer_, self.chat_id_))
            db.commit()
            db.close()
        except sqlite3.Error as error:
            print(error)
        return self.pointer_

    def set_q_idle(self, state):
        self.q_idle_ = state
        try:
            db = sqlite3.connect('survey/participants.db')
            db.execute("UPDATE participants SET q_idle=? WHERE ID=?", (self.q_idle_, self.chat_id_))
            db.commit()
            db.close()
        except sqlite3.Error as error:
            print(error)
        return self.day_

    def set_active(self, state):
        self.active_ = state
        try:
            db = sqlite3.connect('survey/participants.db')
            db.execute("UPDATE participants SET active=? WHERE ID=?", (self.active_, self.chat_id_))
            db.commit()
            db.close()
        except sqlite3.Error as error:
            print(error)
        return self.day_

    def delete_participant(self):
        try:
            db = sqlite3.connect('survey/participants.db')
            db.execute("DELETE FROM participants WHERE ID=?", (self.chat_id_,))
            db.commit()
            db.close()
        except sqlite3.Error as error:
            print(error)
        text = "User:\t" + str(self.chat_id_) + "\tunregistered.\t" + time.strftime("%X %x\n")
        try:
            with open('log.txt', 'a') as log:
                log.write(text)
        except OSError or IOError as error:
            print(error)
        return 0

    def set_next_block(self):
        q_set = self.q_set_
        try:
            block = q_set[self.pointer_]["blocks"][self.block_ + 1]
            self.next_block = [self.pointer_, self.block_ + 1, block]
            return q_set[self.pointer_]["day"]
        except IndexError:
            try:
                block = q_set[self.pointer_ + 1]["blocks"][0]
                self.next_block = [self.pointer_ + 1, 0, block]
                return q_set[self.pointer_ + 1]["day"]
            except IndexError:
                self.next_block = None

    def check_requirements(self, condition):
        if condition == []:
            return True
        for element in condition:
            if element not in self.conditions_:
                return False
        return True



















