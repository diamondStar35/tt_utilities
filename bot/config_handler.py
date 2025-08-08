import gettext
import configparser
import os
import ast
import ctypes
from ctypes import c_int
import sys
import TeamTalk5 as teamtalk
import mpv


class ConfigHandler:
    def __init__(self, config_file="config.ini"):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self.language = "en"
        self._ = gettext.gettext # Initialize _ for default language
        self.custom_username=""

        self.read_config_file()

    def select_language(self):
        locales_dir = "locales"
        available_langs = [lang for lang in os.listdir(locales_dir) if os.path.isdir(os.path.join(locales_dir, lang))]

        if available_langs:
            print("Please choose the language.")
            for i, lang in enumerate(available_langs):
                print(f"{i + 1}. {lang}")

            while True:
                try:
                    choice = int(input("Select language number: ")) - 1
                    if 0 <= choice < len(available_langs):
                        self.language = available_langs[choice]
                        break
                    else:
                        print("Invalid choice.")
                except ValueError:
                    print("Invalid input. Please enter a number.")

        # Install the selected language
        gettext.bindtextdomain("messages", locales_dir)
        gettext.textdomain("messages")  
        try:
            translation = gettext.translation("messages", locales_dir, [self.language])
            translation.install()
            self._ = translation.gettext
        except FileNotFoundError:
            print(f"Language '{self.language}' not found, defaulting to English.")

    def read_config_file(self):
        if not os.path.isfile(self.config_file):
            if sys.platform == "win32":
                import wx
                from bot.gui import ConfigGUI
                app = wx.App()
                gui = ConfigGUI(None, "Configuration")
                app.MainLoop()
            else:
                self.select_language()
                self.create_config_file()
        else:
            self.config.read(self.config_file)

    def create_config_file(self):
        print(self._("Welcome to TeamTalk utilities bot, a powerful bot, not just for spammers"))
        print("\nDeveloped by: Blind masters team")
        print(self._("\nSince it's the first time you open the bot: it will ask you some questions to create the config file, Please follow the instructions carefully and be sure to enter all info correctly."))
        print(self._("\nServer info: "))
        while True:
            server_address = input(self._("Enter server address: "))
            if server_address:
                break
            else:
                print(self._("Error: Server address cannot be blank. Please try again."))
        while True:
            server_port_str = input(self._("Enter server port: ").strip())
            if server_port_str:
                try:
                    server_port = int(server_port_str)
                    break
                except ValueError:
                    print(self._("Error: Invalid server port. Please enter a number."))
            else:
                print(self._("Error: Server port cannot be blank. Please try again."))

        while True:
            print(self._("\nChoose your server type: "))
            print(self._("1: unencrypted server "))
            print(self._("2: encrypted server "))
            try:
                encryption=int(input(self._("Enter your choice: ")))
                if encryption==1:
                    self.encrypted=False
                    break
                elif encryption ==2:
                    self.encrypted=True
                    break
            except ValueError:
                print(self._("Invalid choice "))

        while True:
            server_username = input(self._("Enter bot username: "))
            if server_username:
                break
            else:
                print(self._("Error: username cannot be blank, Please try again "))

        while True:
            server_password = input(self._("Enter bot password: "))
            if server_password:
                break
            else:
                print(self._("Error: Please type the password "))

        print(self._("\nDone, now: Please enter the exclution IP addresses you want to exclude, seperate with a comma between each IP "))
        exclusion_ips = input(self._("Enter exclusion IPs (comma-separated): "))

        while True:
            exclusion_usernames_str = input(self._("Enter usernames to exclude (comma-separated, leave blank to disable): "))
            if exclusion_usernames_str:
                self.exclusion_usernames = exclusion_usernames_str.split(",")
                break
            else:
                self.exclusion_usernames = []
                break

        while True:
            exclusion_nicknames_str = input(self._("Enter nicknames to exclude (comma-separated, leave blank to disable): "))
            if exclusion_nicknames_str:
                self.exclusion_nicknames = exclusion_nicknames_str.split(",")
                break
            else:
                self.exclusion_nicknames = []
                break

        print(self._("\nBot details "))
        while True:
            bot_nickname = input(self._("Enter bot nickname: "))
            if bot_nickname:
                break
            else:
                print(self._("Error: nickname cannot be blank "))

        while True:
            bot_client_name = input(self._("Enter bot client name: "))
            if bot_client_name:
                break
            else:
                print(self._("Client name can't be blank "))

        while True:
            print(self._("\nChoose the bot's gender: "))
            print(self._("1: male"))
            print(self._("2: female"))
            print(self._("3: neutral"))
            try:
                gender_choice=int(input(self._("Enter your choice: ")))
            except:
                print(self._("Error, Invalid choice"))
                continue
            if gender_choice==1:
                self.gender="0"
                break
            elif gender_choice==2:
                self.gender='256'
                break
            elif gender_choice==3:
                self.gender='4096'
                break
            else:
                print(self._("Invalid choice"))

        default_channel=input(self._("Default channel: "))
        if default_channel == "":
            print(self._("Defaulting to root channel"))
            default_channel="/"
        else:
            default_channel=default_channel

        channel_password=input(self._("Channel password: "))

        while True:
            status_message=input(self._("Optionally: Please enter a status message for the bot, Leave blank to set a blank status: "))
            if status_message is not None:
                self.status=status_message
                break
            else:
                self.status=""
                break

        while True:
            vpn_detection_choice=input(self._("Do you want to enable VPN detection? y / n: "))
            if vpn_detection_choice==self._("y").lower():
                vpn_detection=True
                break
            elif vpn_detection_choice==self._("n").lower():
                vpn_detection=False
                break
            else:
                print(self._("Invalid input"))
                continue

        while True:
            prevent_noname_choice=input(self._("Do you want to enable automatic kicking of no name users or users who enter with no name set? Y / N: "))
            if prevent_noname_choice==self._("y").lower():
                prevent_noname=True
                break
            elif prevent_noname_choice==self._("n").lower():
                prevent_noname=False
                break
            else:
                print(self._("Invalid input"))
                continue

        if prevent_noname is False:
            noname_note="Hello. Please set your nickname first by pressing f4 and change it, And then come back. Thank you"
        elif prevent_noname is True:
            noname_note =input(self._("Enter the default note that will be sent to a user who enters with no name set: "))
        if noname_note == "":
            print(self._("Using the default message"))
            noname_note="Hello. Please set your nickname first by pressing f4 and change it, And then come back. Thank you"

        while True:
            intercept_choice=input(self._("Do you want the bot to automatically intercept channel messages for users? This is useful if you want some commands to work regardless of the bot's channel, And also useful for detecting bad words in any other channel the bot is not in: Y / N"))
            if intercept_choice==self._("y").lower():
                intercept_channel_messages=True
                break
            elif intercept_choice==self._("n").lower():
                intercept_channel_messages=False
                break
            else:
                print(self._("Invalid input"))
                continue

        while True:
            jail_users_str = input(self._("Enter usernames to be jailed (comma-separated, leave blank to disable): "))
            if jail_users_str:
                self.jail_users = jail_users_str.split(",")
                break
            else:
                self.jail_users = []
                break

        while True:
            self.jail_channel = input(self._("Enter the jail channel path: "))
            if self.jail_channel:
                break
            elif self.jail_channel=="":
                print(self._("Using the default jail channel: /jail/ "))
                self.jail_channel="/jail/"
                break

        print(self._("Please enter a jail timeout between each attempt if the user trys to joins another channel: this timeout will start, and start counting every time the user joins another channel."))
        print(self._("the jail flood count means how many counts within the specified timeout to ban and kick the user.\nFor example: if the jail timeout is 10, and jail flood count is 5: it means that when the jailed user trys to joins another channel: the bot will move them back, and starts a timer for 10 seconds, within this timer: if the user attempts to leave the jail channel more than 5 times: they will be banned and kicked."))

        while True:
            join_timer_str = input(self._("Specify the jail timeout in seconds (leave blank for default 10): "))
            if join_timer_str:
                try:
                    self.jail_timer_seconds = int(join_timer_str)
                    break
                except ValueError:
                    print(self._("Error: Please enter a valid number."))
            else:
                print(self._("Using the default value 10 "))
                self.jail_timer_seconds = 10
                break

        while True:
            join_count_str = input(self._("Specify the join count threshold (leave blank for default 5): "))
            if join_count_str:
                try:
                    self.jail_flood_count = int(join_count_str)
                    break
                except ValueError:
                    print(self._("Error: Please enter a valid number."))
            else:
                print(self._("Using the default value 5 "))
                self.jail_flood_count = 5
                break

        while True:
            jail_names_str=input(self._("Optionally: Please input jailed nicknames, this is different from jailed users, because this relys on nicknames, while the other option relys on usernames: "))
            if jail_names_str:
                self.jail_names=jail_names_str.split(",")
                break
            else:
                self.jail_names=[]
                break

        print(self._("Please note that the following 2 features are optional, the character limit is to prevent long nicknames, if you want to disable it: enter  0 when asked."))
        try:
            random_message_interval =int(input(self._("Specify the interval between sending messages, Leave blank to disable: ")))
        except:
            random_message_interval=0

        while True:
            char_limit_str=input(self._("Specify how long the name to kick if the name is longer than this limit, Enter 0 to disable: "))
            if char_limit_str:
                try:
                    char_limit=int(char_limit_str)
                    break
                except ValueError:
                    print(self._("Error: Only numbers are allowed here"))

        while True:
            print(self._("\nPlease specify the action when the nickname is longer than the specified char limit: "))
            print(self._("1: Kick the user"))
            print(self._("2: Ban the user"))
            self.char_limit_mode_str=input(self._("Enter your choice: "))
            try:
                self.char_limit_mode=int(self.char_limit_mode_str)
                if self.char_limit_mode in (1, 2):
                    break
            except ValueError:
                print(self._("Error, Only numbers are allowed here"))

        while True:
            print(self._("\nChoose the action when a black listed nickname is in the blacklist file"))
            print(self._("1: Kick the user"))
            print(self._("2: Ban the user"))
            self.blacklist_mode_str=input(self._("Enter your choice: "))
            try:
                self.blacklist_mode=int(self.blacklist_mode_str)
                if self.blacklist_mode in (1,2):
                    break
            except ValueError:
                print(self._("Invalid choice, Only numbers are allowed here"))

        video_deletion_timer_str=input(self._("Please specify the timer before deleting a youtube video, In minutes. Set to 0 to disable automatic video deletion after upload: "))
        if video_deletion_timer_str=="":
            print(self._("Defaulting to 15 minutes."))
            video_deletion_timer=15
        else:
            if int(video_deletion_timer_str) >= 0:
                video_deletion_timer=int(video_deletion_timer_str)
            else:
                print(self._("Defaulting to 15 minutes."))
                video_deletion_timer=15

        banned_countries_str =input(self._("Enter the list of disallowed countries. Separated with commas: "))
        if banned_countries_str:
            banned_countries=banned_countries_str.split(",")
        else:
            banned_countries=[]

        print(self._("\nAudio Device Selection:"))
        
        print(self._("Available Input Devices:"))
        input_devices = self.get_input_devices(teamtalk.SoundDevice.nMaxInputChannels)
        for i, device in enumerate(input_devices):
            print(f"{i+1}. {teamtalk.ttstr(device.szDeviceName)}")

        while True:
            try:
                input_choice = int(input(self._("Choose Input Device Number: "))) - 1
                if 0 <= input_choice < len(input_devices):
                    input_device_id = input_devices[input_choice].nDeviceID
                    break
                else:
                    print(self._("Invalid choice. Please enter a valid number from the list."))
            except ValueError:
                print(self._("Invalid input. Please enter a number."))

        print(self._("\nAvailable Output Devices:"))
        output_devices = self.get_mpv_output_devices()
        for i, device in enumerate(output_devices):
            print(f"{i+1}. {device['description']}")

        while True:
            try:
                output_choice = int(input(self._("Choose Output Device Number: "))) - 1
                if 0 <= output_choice < len(output_devices):
                    output_device_index = output_choice
                    break
                else:
                    print(self._("Invalid choice. Please enter a valid number from the list."))
            except ValueError:
                print(self._("Invalid input. Please enter a number."))

        seek_step_str=input(self._("Seek step, in seconds. Default is 5: "))
        if seek_step_str =="":
            seek_step=5
        else:
            seek_step=int(seek_step_str)

        default_volume_str=input(self._("Default volume: "))
        if default_volume_str=="":
            default_volume=80
        else:
            default_volume=int(default_volume_str)

        max_volume_str=input(self._("Max volume: Default is 100: "))
        if max_volume_str=="":
            max_volume = 100
        else:
            max_volume=int(max_volume_str)

        print(self._("\nThe following section is completely optional. If you want to enable other features of the bot: Please fill the required info below: "))
        telegram_bot_token=input(self._("Please enter a telegram bot token. This is optional: "))

        weather_api_key=input(self._("Enter your weather API key, Please read the readme file for more info on how to get one: "))

        print(self._("\nSSH info, Note: this section is made because in case you want to interact with your SSH server from your bot, and you may skip it if you don't have a server, read the readme file for more info "))
        print(self._("We do not collect such info or share it, because the bot is completely controled by you and no one else, the bot is not connected to any servers to track users or bans them from accessing the bot, Just a reminder in case you're worried about your server info "))
        ssh_hostname = input(self._("Enter SSH hostname: "))
        ssh_port_str = input(self._("Enter SSH port: "))
        if ssh_port_str:
            try:
                ssh_port=int(ssh_port_str)
            except ValueError:
                pass
        else:
            ssh_port=22

        ssh_username = input(self._("Enter SSH username: "))
        ssh_password = input(self._("Enter SSH password: "))
        allowed_ips=input(self._("Enter the list of allowed IP addresses to execute ssh commands: "))

        print(self._("\nAuthorized usernames or admins: those who can control your SSH server from your bot, you may skip it if you don't have an SSH server"))
        authorized_users = input(self._("Enter authorized usernames (comma-separated): "))

        while True:
            detect_admins_choice=input(self._("Do you want the bot to automatically detect server administrators as authorized users? y / n: "))
            if detect_admins_choice==self._("y").lower():
                detect_server_admins=True
                break
            elif detect_admins_choice==self._("n").lower():
                detect_server_admins=False
                break
            else:
                print(self._("Invalid input"))
                continue

        while True:
            print(self._("\nChoose detection mode for accounts: "))
            print(self._("1: guest accounts"))
            print(self._("2: All accounts"))
            print(self._("3: Custom userName account"))
            mode = input(self._("Enter your choice: "))
            if mode in ("1", "2", "3"):
                detection_mode = int(mode)
                break
            else:
                print(self._("Invalid choice. Please enter 1, 2, or 3."))

        if detection_mode == 3:
            self.custom_username = input(self._("Enter the custom username to detect: "))

        print(self._("\nTeamTalk license. Skip this section if you don't have a license"))
        license_name=input(self._("License name: "))
        license_key=input(self._("License key: "))

        config = configparser.ConfigParser()
        config["server"] = {
            "address": server_address,
            "port": server_port,
            "encrypted": self.encrypted,
            "username": server_username,
            "password": server_password,
        }
        config["bot"] = {
            "nickname": bot_nickname,
            "client_name": bot_client_name,
            "gender": self.gender,
            "language": self.language,
            "default_channel": default_channel,
            "channel_password": channel_password,
            "status_message": self.status,
            "vpn_detection": vpn_detection,
            "prevent_noname": prevent_noname,
            "noname_note": noname_note,
            "intercept_channel_messages": intercept_channel_messages,
            "jail_users": ",".join(self.jail_users),
            "jail_names": ",".join(self.jail_names),
            "jail_channel": self.jail_channel,
            "jail_timer_seconds": self.jail_timer_seconds,
            "jail_flood_count": self.jail_flood_count,
            "random_message_interval": random_message_interval,
            "char_limit": char_limit,
            "char_limit_mode": self.char_limit_mode,
            "blacklist_mode": self.blacklist_mode,
            "video_deletion_timer": video_deletion_timer,
            "banned_countries": ",".join(banned_countries),
        }
        config["playback"] = {
            "input_device": input_device_id,
            "output_device": output_device_index,
            "seek_step": seek_step,
        "default_volume": default_volume,
        "max_volume": max_volume,
        }
        config["telegram"] = {
            "telegram_bot_token": telegram_bot_token,
        }
        config["exclusion"] = {
            "ips": exclusion_ips,
            "usernames": ",".join(self.exclusion_usernames), 
            "nicknames": ",".join(self.exclusion_nicknames), 
        }
        config["accounts"] = {
            "detection_mode": detection_mode,
            "custom_username": self.custom_username,
            "authorized_users": authorized_users,
        "detect_server_admins": detect_server_admins
        }
        config["weather"] = {"api_key": weather_api_key}
        config["ssh"] = {
            "hostname": ssh_hostname,
            "port": ssh_port,
            "username": ssh_username,
            "password": ssh_password,
            "allowed_ips": allowed_ips
        }
        config["teamtalk_license"]= {
            "license_name": license_name,
            "license_key": license_key,
        }
        with open("config.ini", "w") as configfile:
            config.write(configfile)
            print(self._("\nCreated the config file"))
        self.config.read(self.config_file)

    def get_input_devices(self, channel_type):
        """Returns a list of audio devices based on channel type."""
        tt = teamtalk.TeamTalk()
        devices = tt.getSoundDevices()
        filtered_devices = [device for device in devices if getattr(device, "nMaxInputChannels" if channel_type == teamtalk.SoundDevice.nMaxInputChannels else "nMaxOutputChannels") > 0]
        tt.closeTeamTalk()
        return filtered_devices

    def get_mpv_output_devices(self):
        """Returns a list of output devices from mpv."""
        player = mpv.MPV()
        devices = player.audio_device_list
        player.terminate()
        return devices

    def get_server_config(self):
        try:
            server_section = self.config["server"]
            return {
                "address": server_section.get("address"),
                "port": server_section.getint("port"),
                "encrypted": ast.literal_eval(server_section.get("encrypted")),
                "username": server_section.get("username"),
                "password": server_section.get("password"),
            }
        except (configparser.Error, KeyError, configparser.NoSectionError, configparser.NoOptionError, ValueError) as e:
            print(self._(f"Config file error: {e}"))
            print(self._("Note: this error likely due to a missing part of the config file, Please delete your existing config file and create it again, If this issue persists: Please contact us"))
            sys.exit(1)

    def get_bot_config(self):
        try:
            bot_section = self.config["bot"]
            return {
                "nickname": bot_section.get("nickname"),
                "client_name": bot_section.get("client_name"),
                "gender": bot_section.getint("gender"),
                "language": bot_section.get("language"),
                "default_channel": bot_section.get("default_channel"),
                "channel_password": bot_section.get("channel_password"),
                "status_message": bot_section.get("status_message"),
                "vpn_detection": bot_section.getboolean("vpn_detection"),
                "prevent_noname": bot_section.getboolean("prevent_noname"),
                "noname_note": bot_section.get("noname_note"),
                "intercept_channel_messages": bot_section.getboolean("intercept_channel_messages"),
                "jail_users": bot_section.get("jail_users", "").split(","),
                "jail_names": bot_section.get("jail_names", "").split(","),
                "jail_channel": bot_section.get("jail_channel"),
                "jail_timer_seconds": bot_section.getint("jail_timer_seconds", 10),
                "jail_flood_count": bot_section.getint("jail_flood_count", 5),
                "random_message_interval": bot_section.getint("random_message_interval", 0),
                "char_limit": bot_section.getint("char_limit"),
                "char_limit_mode": bot_section.getint("char_limit_mode"),
                "blacklist_mode": bot_section.getint("blacklist_mode"),
                "video_deletion_timer": bot_section.getint("video_deletion_timer"),
                "banned_countries": bot_section.get("banned_countries", "").split(","),
            }
        except (configparser.Error, KeyError, configparser.NoSectionError, configparser.NoOptionError, ValueError) as e:
            print(self._(f"Config file error: {e}"))
            print(self._("Note: this error likely due to a missing part of the config file, Please delete your existing config file and create it again, If this issue persists: Please contact us"))
            sys.exit(1)

    def get_playback_config(self):
        try:
            playback_section = self.config["playback"]
            return {
                "input_device": playback_section.getint("input_device"),
                "output_device": playback_section.getint("output_device"),
                "seek_step": playback_section.getint("seek_step"),
                "default_volume": playback_section.getint("default_volume"),
                "max_volume": playback_section.getint("max_volume"),
            }
        except (configparser.Error, KeyError, configparser.NoSectionError, configparser.NoOptionError, ValueError) as e:
            print(self._(f"Config file error: {e}"))
            print(self._("Note: this error likely due to a missing part of the config file, Please delete your existing config file and create it again, If this issue persists: Please contact us"))
            sys.exit(1)

    def get_telegram_config(self):
        try:
            telegram_section = self.config["telegram"]
            return {
                "telegram_bot_token": telegram_section.get("telegram_bot_token"),
            }
        except (configparser.Error, KeyError, configparser.NoSectionError, configparser.NoOptionError, ValueError) as e:
            print(self._(f"Config file error: {e}"))
            print(self._("Note: this error likely due to a missing part of the config file, Please delete your existing config file and create it again, If this issue persists: Please contact us"))
            sys.exit(1)

    def get_exclusion_config(self):
        try:
            exclusion_section = self.config["exclusion"]
            return {
                "ips": exclusion_section.get("ips").split(","),
                "usernames": exclusion_section.get("usernames", "").split(","),
                "nicknames": exclusion_section.get("nicknames", "").split(","),
            }
        except (configparser.Error, KeyError, configparser.NoSectionError, configparser.NoOptionError, ValueError) as e:
            print(self._(f"Config file error: {e}"))
            print(self._("Note: this error likely due to a missing part of the config file, Please delete your existing config file and create it again, If this issue persists: Please contact us"))
            sys.exit(1)

    def get_accounts_config(self):
        try:
            accounts_section = self.config["accounts"]
            return {
                "detection_mode": accounts_section.getint("detection_mode"),
                "custom_username": accounts_section.get("custom_username"),
                "authorized_users": accounts_section.get("authorized_users", "").split(","),
                "detect_server_admins": accounts_section.getboolean("detect_server_admins"),
            }
        except (configparser.Error, KeyError, configparser.NoSectionError, configparser.NoOptionError, ValueError) as e:
            print(self._(f"Config file error: {e}"))
            print(self._("Note: this error likely due to a missing part of the config file, Please delete your existing config file and create it again, If this issue persists: Please contact us"))
            sys.exit(1)

    def get_weather_config(self):
        try:
            weather_section = self.config["weather"]
            return weather_section.get("api_key")
        except (configparser.Error, KeyError, configparser.NoSectionError, configparser.NoOptionError, ValueError) as e:
            print(self._(f"Config file error: {e}"))
            print(self._("Note: this error likely due to a missing part of the config file, Please delete your existing config file and create it again, If this issue persists: Please contact us"))
            sys.exit(1)

    def get_ssh_config(self):
        try:
            ssh_section = self.config["ssh"]
            return {
                "hostname": ssh_section.get("hostname"),
                "port": ssh_section.getint("port"),
                "username": ssh_section.get("username"),
                "password": ssh_section.get("password"),
                "allowed_ips": ssh_section.get("allowed_ips", "").split(",")
            }
        except (configparser.Error, KeyError, configparser.NoSectionError, configparser.NoOptionError, ValueError) as e:
            print(self._(f"Config file error: {e}"))
            print(self._("Note: this error likely due to a missing part of the config file, Please delete your existing config file and create it again, If this issue persists: Please contact us"))
            sys.exit(1)

    def get_teamtalk_license_config(self):
        try:
            teamtalk_license_section = self.config["teamtalk_license"]
            return {
                "license_name": teamtalk_license_section.get("license_name"),
                "license_key": teamtalk_license_section.get("license_key"),
            }
        except (configparser.Error, KeyError, configparser.NoSectionError, configparser.NoOptionError, ValueError) as e:
            print(self._(f"Config file error: {e}"))
            print(self._("Note: this error likely due to a missing part of the config file, Please delete your existing config file and create it again, If this issue persists: Please contact us"))
            sys.exit(1)

    def save_bot_config(self, bot_config):
        """Saves the bot configuration to the config file."""
        try:
            self.config["bot"] = {
                "nickname": bot_config["nickname"],
                "client_name": bot_config["client_name"],
                "gender": bot_config["gender"],
                "language": bot_config["language"],
                "default_channel": bot_config['default_channel'],
                "channel_password": bot_config['channel_password'],
                "status_message": bot_config["status_message"],
                "vpn_detection": bot_config['vpn_detection'],
                "prevent_noname": bot_config['prevent_noname'],
                "noname_note": bot_config['noname_note'],
                "intercept_channel_messages": bot_config['intercept_channel_messages'],
                "jail_users": ",".join(bot_config["jail_users"]),
                "jail_names": ",".join(bot_config["jail_names"]),
                "jail_channel": bot_config["jail_channel"],
                "jail_timer_seconds": bot_config["jail_timer_seconds"],
                "jail_flood_count": bot_config["jail_flood_count"],
                "random_message_interval": bot_config["random_message_interval"],
                "char_limit": bot_config["char_limit"],
                "char_limit_mode": bot_config["char_limit_mode"],
                "blacklist_mode": bot_config["blacklist_mode"],
                "video_deletion_timer": bot_config["video_deletion_timer"],
                "banned_countries": ",".join(bot_config["banned_countries"]),
            }

            with open(self.config_file, "w") as configfile:
                self.config.write(configfile)
        except (configparser.Error, KeyError) as e:
            print(self._(f"Error saving bot config: {e}"))