import time
from concurrent.futures import ThreadPoolExecutor
from deep_translator import GoogleTranslator
from TeamTalk5 import TextMessage, TextMsgType, ttstr

class TranslatorCog:
    """
    A module for handling all translation related commands and logic.
    """
    def __init__(self, bot):
        self.bot = bot
        self._ = bot._
        self.translation_pool = self.bot.quick_task_pool        
        self.auto_translate = False
        self.source_lang = 'auto'
        self.target_lang = 'en'
        self.last_translated_message = None
        self.user_translation_modes = {}
        self.user_translation_cooldowns = {}
        self.last_t_command_time = 0

    def register(self, command_handler):
        """Registers all the translator commands."""
        command_handler.register_command('t', self.handle_t_command, help_text=self._("Toggles auto-translation for channel messages. Usage: /t <source_language_code> <target_language_code>. If the mode is already active, send /t again without arguments to disable."))
        command_handler.register_command('pt', self.handle_pt_command, help_text=self._("Toggles private translation mode for you. Usage: /pt <source_language_code> <target_language_code>. If the mode is already active, send /pt again without arguments to disable."))

    def on_user_parted(self, user):
        """Cleans up translation state when a user leaves."""
        user_id = user.nUserID
        if user_id in self.user_translation_modes:
            del self.user_translation_modes[user_id]
        if user_id in self.user_translation_cooldowns:
            del self.user_translation_cooldowns[user_id]

    def handle_channel_translation(self, textmessage: TextMessage):
        """If auto-translation is on, submits the message for translation."""
        sender = self.bot.getUser(textmessage.nFromUserID)
        is_bot_message = ttstr(textmessage.szFromUsername) == self.bot.server_config["username"] and \
                         ttstr(sender.szNickname) == self.bot.bot_config["nickname"]

        if not is_bot_message and self.auto_translate and \
           (textmessage.nMsgType in [TextMsgType.MSGTYPE_CHANNEL, TextMsgType.MSGTYPE_BROADCAST]):
            self.translation_pool.submit(self._translate_and_send_channel, textmessage)
            return True
        return False

    def handle_private_translation(self, textmessage: TextMessage):
        """If a user is in private translate mode, submits the message for translation."""
        user_id = textmessage.nFromUserID
        if textmessage.nMsgType == TextMsgType.MSGTYPE_USER and user_id in self.user_translation_modes:
            if user_id in self.user_translation_cooldowns and time.time() - self.user_translation_cooldowns.get(user_id, 0) < 1.3:
                return True # Cooldown active, message handled (ignored)
            
            self.user_translation_cooldowns[user_id] = time.time()
            self.translation_pool.submit(self._translate_and_send_private, textmessage)
            return True
        return False
        
    def _translate_and_send_channel(self, textmessage: TextMessage):
        """Worker thread for channel translation."""
        message_text = ttstr(textmessage.szMessage)
        if message_text == self.last_translated_message:
            return

        try:
            translated = GoogleTranslator(source=self.source_lang, target=self.target_lang).translate(message_text)
            if translated:
                self.bot.send_message(f"{translated}")
                self.last_translated_message = message_text
        except Exception as e:
            self.bot.send_message(self._("Error during translation: {e}. Disabling auto-translate.").format(e=e))
            self.auto_translate = False

    def _translate_and_send_private(self, textmessage: TextMessage):
        """Worker thread for private translation."""
        user_id = textmessage.nFromUserID
        translation_mode = self.user_translation_modes.get(user_id)
        if not translation_mode:
            return

        user = self.bot.getUser(user_id)
        if not user or user.nChannelID != self.bot.getMyChannelID():
            del self.user_translation_modes[user_id]
            self.bot.privateMessage(user_id, self._("Private translate mode disabled as you are no longer in the same channel as the bot."))
            return

        try:
            translated = GoogleTranslator(
                source=translation_mode["source"], target=translation_mode["target"]
            ).translate(ttstr(textmessage.szMessage))
            if translated:
                self.bot.send_message(self._("{nickname} says: {translated}").format(nickname=ttstr(user.szNickname), translated=translated))
        except Exception as e:
            self.bot.privateMessage(user_id, self._("Error: {e}. Disabling private translate mode.").format(e=e))
            if user_id in self.user_translation_modes:
                del self.user_translation_modes[user_id]

    def handle_t_command(self, textmessage, *args):
        """Toggles auto-translation for channel messages."""
        if self.auto_translate:
            self.auto_translate = False
            self.bot.send_message(self._("Auto-translation disabled."))
        else:
            self.auto_translate = True
            if len(args) >= 2:
                self.source_lang, self.target_lang = args[0], args[1]
            self.bot.send_message(self._("Auto-translation enabled from {source} to {target}.").format(source=self.source_lang, target=self.target_lang))

    def handle_pt_command(self, textmessage, *args):
        """Toggles private translation mode for a user."""
        user_id = textmessage.nFromUserID
        if user_id in self.user_translation_modes:
            del self.user_translation_modes[user_id]
            self.bot.privateMessage(user_id, self._("Private translate mode disabled."))
        else:
            if len(args) < 2:
                self.bot.privateMessage(user_id, self._("Usage: /pt <source_lang> <target_lang>"))
                return
            self.user_translation_modes[user_id] = {"source": args[0], "target": args[1]}
            self.bot.privateMessage(user_id, self._("Private translate mode enabled from {source} to {target}.").format(source=args[0], target=args[1]))
