import sqlite3
import pickle

from datetime import datetime
from pytz import timezone


from admin.settings import SCHEDULE_INTERVALS
from admin.debug import debug

from telegram import Bot, Update, ReplyKeyboardMarkup, ReplyKeyboardHide
from telegram.ext import Job, JobQueue

from survey.data_set import DataSet
from survey.participant import Participant
from survey.keyboard_presets import CUSTOM_KEYBOARDS
import survey.keyboard_presets as kbps

import random

LANGUAGE, COUNTRY, GENDER, TIME_T, TIME_OFFSET = range(5)


# Calculates seconds until a certain hh:mm
# event. Used for the job_queue mainly.
# Timezones are already handled # Todo
def calc_delta_t(time, days, time_zone=None):
    hh = time[:2]
    mm = time[3:]

    current = datetime.now()
    future = datetime(current.year, current.month, current.day, int(hh), int(mm))
    seconds = future - current
    if days > 0 and seconds.seconds < 86400:
        return seconds.seconds + 86400 + ((days - 1) * 86400)
    elif days > 0 and seconds.seconds > 86400:
        return seconds.seconds + ((days - 1) * 86400)
    else:
        return seconds.seconds


# Generates a random time offset
# for the next block that shall be scheduled.
# The intervals are defined in admin/settings.py
def calc_block_time(time_t):
    try:
        interval = SCHEDULE_INTERVALS[time_t]
    except KeyError:
        return 0  # Todo

    hh_start = int(interval[0][:2])
    hh_end = int(interval[1][:2])
    mm_begin = int(interval[0][3:])
    mm_end = int(interval[1][3:])

    if hh_start < hh_end:
        value_hh = random.randint(hh_start, hh_end)
        if value_hh == hh_start:
            value_mm = random.randint(mm_begin + 10, 59)
        elif value_hh == hh_end:
            value_mm = random.randint(0, mm_end)
        else:
            value_mm = random.randint(0, 59)

    elif hh_start == hh_end:
        value_hh = hh_start
        value_mm = random.randint(mm_begin + 10, mm_end - 10)
    else:
        value_hh = random.choice[random.randint(hh_start, 23), random.randint(0, hh_end)]
        if value_hh == hh_start:
            value_mm = random.randint(mm_begin + 10, 59)
        elif value_hh == hh_end:
            value_mm = random.randint(0, mm_end)
        else:
            value_mm = random.randint(0, 59)

    return str(value_hh).zfill(2) + ':' + str(value_mm).zfill(2)


# This function does the main handling of
# user questions and answers.
# This is function is registered in the Dispatcher.
def question_handler(bot: Bot, update: Update, user_map: DataSet, job_queue: JobQueue):
    try:
        # Get the user from the dict and its question_set (by language)
        user = user_map.participants[update.message.chat_id]  # type: Participant

        # Case for very first question.
        if user.question_ == -1:
            user.set_active(True)
            user.set_language(update.message.text)
            user.set_block(0)
            q_set = user_map.return_question_set_by_language(user.language_)
            user.q_set_ = q_set
            current_day = q_set[0]["day"]
            user.set_day(current_day)
            user.set_block(0)
        elif user.q_idle_:
            q_set = user.q_set_
            # Get the matching question for the users answer.

            pointer = user.pointer_
            d_prev = q_set[pointer]

            b_prev = d_prev["blocks"][user.block_]
            q_prev = b_prev["questions"][user.question_]

            if not valid_answer(q_prev, update.message.text):
                user.set_q_idle(True)
                return
            # Storing the answer and moving on the next question

            store_answer(user, update.message.text, q_prev)
            # Todo check last question
            user.set_q_idle(False)
        else:
            # User has send something without being asked a question.
            return
    except KeyError as error:
        print(error)
        return

    question = find_next_question(user)
    if question is not None:
        message = question["text"]
        q_keyboard = get_keyboard(question["choice"])
        bot.send_message(chat_id=user.chat_id_, text=message, reply_markup=q_keyboard)
        user.set_q_idle(True)
    else:
        user.block_complete_ = True
        next_day = user.set_next_block()
        element = user.next_block[2]
        day_offset = next_day - user.day_
        time_t = calc_block_time(element["time"])
        due = calc_delta_t(time_t, day_offset)

        new_job = Job(queue_next, due, repeat=False, context=[user, job_queue])
        job_queue.put(new_job)


# This function is getting used to generate
# the CSV files and store values.
# Also the conditions, DB values get set here.
def store_answer(user, message, question):
    commands = question['commands']
    for [element] in commands:
        # -- DB TRIGGER for storing important user data -- #
        if element == "COUNTRY":
            user.set_country(message)
        elif element == "TZ_OFFSET":
            user.set_tz(message)
        elif element == "GENDER":
            user.set_gender(message)

    condition = question["condition"]
    if condition != [] and message in condition[0]:
        user.add_conditions(condition)
    # Todo: CSV stuff
    return


# This function is called by the job_queue
# and starts all the blocks after the set time.
# It also calls itself recursively to assure progressing.
def queue_next(bot: Bot, job: Job):
    user = job.context[0]  # type: Participant
    job_queue = job.context[1]
    if not user.active_:
        return
    user.block_complete_ = False
    user.set_question(0)
    user.set_pointer(user.next_block[0])
    user.set_block(user.next_block[1])
    element = user.next_block[2]

    # Check if the user is currently active
    if not user.active_:
        return

    try:
        # Find next question that the user should get.
        while not user.check_requirements(element["questions"][user.question_]):
            user.increase_question()
    except IndexError:
        # User did not fulfill any questions for the day so we reschedule.
        # Set the new day.
        next_day = user.set_next_block()
        if user.next_block is None:
            return finished(user, job_queue)

        element = user.next_block[2]
        day_offset = next_day - user.day_
        time_t = calc_block_time(element["time"])
        due = calc_delta_t(time_t, day_offset)

        # Add new job and to queue. The function basically calls itself recursively after x seconds.
        new_job = Job(queue_next, due, repeat=False, context=[user, job_queue])
        job_queue.put(new_job)
        return

    # Sending the question
    question = element["questions"][user.question_]

    q_text = question["text"]
    q_keyboard = get_keyboard(question["choice"])
    bot.send_message(user.chat_id_, q_text, reply_markup=q_keyboard)
    user.set_q_idle(True)

    # Check if there is a reason to queue again.
    if not user.auto_queue_ or not user.block_complete_:
        return

    # Calculate seconds until question is due.
    next_day = user.set_next_block()
    if user.next_block is None:
        return finished(user, job_queue)
    element = user.next_block[2]
    day_offset = next_day - user.day_
    time_t = calc_block_time(element["time"])
    due = calc_delta_t(time_t, day_offset)

    new_job = Job(queue_next, due, repeat=False, context=[user, job_queue])
    job_queue.put(new_job)
    return


# This function returns the next
# question meant for the user.
# If the block is complete None is returned.
def find_next_question(user):
    q_set = user.q_set_
    try:
        q_day = q_set[user.pointer_]
        q_block = q_day["blocks"][user.block_]
        question = q_block["questions"]
        user.increase_question()
        while not user.check_requirements(question[user.question_]):
            user.increase_question()
        return question[user.question_]
    except IndexError:
        return None


# This function returns the ReplyKeyboard for the user.
# Either the ones from the json file are used or
# more complex ones are generated in survey/keyboard_presets.py
def get_keyboard(choice):
    if choice == []:
        return ReplyKeyboardHide()

    # -------- Place to register dynamic keyboards -------- #
    if choice[0][0] == 'KB_TZ_OFFSET':
        return ReplyKeyboardMarkup(kbps.generate_timezone_kb(user.country_))

    try:
        keyboard = ReplyKeyboardMarkup(CUSTOM_KEYBOARDS[choice[0][0]])
    except KeyError:
        keyboard = ReplyKeyboardMarkup(choice)

    return keyboard


# If the command FORCE_KB_REPLY is set in json the
# answer is checked if it is really a choice
# from the ReplyKeyboard.
def valid_answer(question, message):
    commands = question['commands']
    if ['FORCE_KB_REPLY'] not in commands or question['choice'] == []:
        return True
    try:
        choice = CUSTOM_KEYBOARDS[question['choice'][0][0]]
    except KeyError:
        choice = question['choice']

    if [message] in choice:
        return True
    else:
        return False


# This functions handles the very last question.
# It allows the user to finish its question within
# 24 hours. Afterwards finalize() is called.
def finished(user, job_queue):
    user.last_ = True
    new_job = Job(finalize, 86400, repeat=False, context=user)
    job_queue.put(new_job)
    return


# If the user reaches this function he has successfully
# completed the survey. The clean up is done here
# and the he gets set to passive.
def finalize(bot: Bot, job: Job):
    user = job.context
    user.set_active = False
    # Todo File saving, maybe a final message
    return


# This function gets called at program start to load in
# all users from the DB. This function ensures that random
# crashes of the program are not an issue and no data loss occurs.
def initialize_participants(job_queue: JobQueue):
    user_map = DataSet()
    try:
        db = sqlite3.connect('survey/participants.db')
        cursor = db.cursor()
        cursor.execute("SELECT * FROM participants ORDER BY (ID)")
        participants = cursor.fetchall()
        # print(participants)
        for row in participants:
            user = Participant(row[0], init=False)
            user.conditions_ = pickle.loads(row[1])
            user.time_t_ = row[2]
            user.country_ = row[3]
            user.gender_ = row[4]
            user.language_ = row[5]
            user.question_ = row[6]
            user.tz_ = row[7]
            user.day_ = row[8]
            user.q_idle_ = row[9]
            user.active_ = row[10]
            user.block_ = row[11]
            user.pointer_ = row[12]
            user_map.participants[row[0]] = user

            if user.language_ != '':
                q_set = user_map.return_question_set_by_language(user.language_)
                user.q_set_ = q_set
                if user.question_ != -1:
                    user.set_next_block()
                    next_day = user.set_next_block()
                    element = user.next_block[2] # Todo
                    day_offset = next_day - user.day_
                    time_t = calc_block_time(element["time"])
                    due = calc_delta_t(time_t, day_offset)

                    new_job = Job(queue_next, due, repeat=False, context=[user, job_queue])
                    job_queue.put(new_job)
            else:
                user.next_block = None
                if user.active_ and user.pointer_ > -1:
                    finished(user, job_queue)
    except sqlite3.Error as error:
        print(error)
    return user_map


