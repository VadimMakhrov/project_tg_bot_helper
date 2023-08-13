import logging


class Logger:
    def __init__(self):
        logging.basicConfig(level=logging.INFO, filename="tg_bot.log", filemode="a",
                            format="%(asctime)s %(levelname)s %(message)s")

    def log_obj(self, ob):
        logging.info(f'object: {ob}, type: {type(ob)}')

    def log_message(self, message):
        logging.info(f'message.chat.id: {message.chat.id}, user: {message.from_user.first_name}, text: {message.text}')

    def log_keyboard(self, markup):
        logging.info(f'markup.keyboard: {markup.keyboard}')

    def log_position(self, current_position):
        logging.info(f'current_position: {current_position}')

    def log_params_current(self, params_current):
        logging.info(f'params_current: {params_current}')

    def log_picture(self,picture):
        logging.info(f'picture type: {type(picture)}')
