# Keywords:
#
# Commands:
# FORCE_KB_REPLY    : The user has to choose an option from the Keyboard to proceed.
# AUTO_QUEUE_OF     : Deactivates the auto_queue. There will be no automatic scheduling for the next day if the user
#                     does no answer all questions.
# AUTO_QUEUE_ON     : Activates the auto_queue. Even if the user did not answer all questions the questions for
#                     the next day will be scheduled.
#
# COUNTRY           : Signals, that the user will respond with his country: Relevant for database.
# AGE               : -- || --
# GENDER            : -- || --
# TZ_OFFSET         : -- || --
# TIME              : -- || --
#
# Special Keyboards:
# KB_EMOJI_SCALE_5  : Emoji Keyboard with 5 levels of mood
# KB_COUNTRY        : Country keyboard
# KB_TZ_OFFSET      : For retrieving the Timezone Offset

# List of chat_ids that are admins
ADMINS = ['0x0', '0x0']

# Debug mode on/off
DEBUG = True

# Default language if something goes wrong.
DEFAULT_LANGUAGE = 'de'

# Scheduling intervals for question blocks.
SCHEDULE_INTERVALS = {
                        "RANDOM_1": ["08:00", "12:00"],
                        "RANDOM_2": ["13:00", "15:00"],
                        "RANDOM_3": ["16:00", "20:00"]
                     }

DB_TRIGGER = {

             }




