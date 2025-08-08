import wx
import configparser
import webbrowser
import TeamTalk5 as teamtalk
import mpv
import gettext
import os


class ConfigGUI(wx.Frame):
    def __init__(self, parent, title):
        super().__init__(parent, title=title)
        self.current_section = 0
        self.language = "en"
        self._ = gettext.gettext # Initialize _ for default language

        self.sections = [
            {"label": "Language Selection", "fields": [
                {"name": "language", "type": "language", "label": "Select Language", "default": "en"}
            ]},
            {"label": "Server Config", "fields": [
                {"name": "server_address", "type": "text", "label": self._("Server Address"), "default": ""},
                {"name": "server_port", "type": "int", "label": self._("Server Port"), "default": "10333"},
                {"name": "server_encrypted", "type": "bool", "label": self._("Encrypted server"), "default": False},
                {"name": "server_username", "type": "text", "label": self._("Bot Username"), "default": ""},
                {"name": "server_password", "type": "password", "label": self._("Bot Password"), "default": ""}
            ]},
            {"label": "Bot Settings", "fields": [
                {"name": "bot_nickname", "type": "text", "label": self._("Bot Nickname"), "default": ""},
                {"name": "bot_client_name", "type": "text", "label": self._("Bot Client Name"), "default": ""},
                {"name": "bot_gender", "type": "radio", "label": self._("Bot Gender"), "options": [self._("Male"), self._("Female"), self._("Neutral")], "default": self._("Male")},
                {"name": "default_channel", "type": "text", "label": self._("Default channel to join after login: "), "default": "/"},
                {"name": "channel_password", "type": "text", "label": self._("Channel password"), "default": ""},
                {"name": "bot_status_message", "type": "text", "label": self._("Bot Status Message"), "default": ""},
                {"name": "vpn_detection", "type": "bool", "label": self._("Enable VPN detection"), "default": True},
                {"name": "prevent_noname", "type": "bool", "label": self._("Automatically kick users with no name"), "default": True},
                {"name": "noname_note", "type": "text", "label": self._("Default message that will be sent to users with no name when they login"), "default": "Hello. Please set your nickname first by pressing f4 and change it, And then come back. Thank you"},
                {"name": "intercept_channel_messages", "type": "bool", "label": self._("Enable intercepting channel messages for all users: Useful for detecting bad words in all channels as well as allowing some commands to work regardless of the bot's channel"), "default": True},
                {"name": "jail_users", "type": "text", "label": self._("Jail Users (comma-separated)"), "default": ""},
                {"name": "jail_names", "type": "text", "label": self._("Jail Nicknames (comma-separated)"), "default": ""},
                {"name": "jail_channel", "type": "text", "label": self._("Jail Channel Path"), "default": "/jail"},
                {"name": "jail_timer_seconds", "type": "int", "label": self._("Jail Timeout (seconds)"), "default": 10},
                {"name": "jail_flood_count", "type": "int", "label": self._("Jail Flood Count"), "default": 5},
                {"name": "random_message_interval", "type": "int", "label": self._("Random Message Interval"), "default": 0},
                {"name": "char_limit", "type": "int", "label": self._("Character Limit for Nicknames"), "default": 0},
                {"name": "char_limit_mode", "type": "radio", "label": self._("Action for Long Nicknames"), "options": [self._("Kick the user"), self._("Ban the user")], "default": self._("Kick the user")},
                {"name": "blacklist_mode", "type": "radio", "label": self._("Action for Blacklisted Nicknames or words"), "options": [self._("Kick the user"), self._("Ban the user")], "default": self._("Kick the user")},
                {"name": "video_deletion_timer", "type": "int", "label": self._("Specify the timer for automatic video deletion after upload. Set it to 0 to disable automatic deleting of uploaded videos."), "default": 15},
                {"name": "banned_countries", "type": "text", "label": self._("Specify the list of banned or disallowed countries from entering the server. Separated with comma."), "default": ""},
            ]},
            {"label": "Playback settings", "fields": [
                {"name": "input_device_id", "type": "input_device", "label": self._("Input Device"), "default": None},
                {"name": "output_device_id", "type": "output_device", "label": self._("Output Device"), "default": None},
                {"name": "seek_step", "type": "int", "label": self._("Seek step, in seconds: "), "default": 5},
                {"name": "default_volume", "type": "int", "label": self._("Default volume"), "default": 80},
                {"name": "max_volume", "type": "int", "label": self._("Max volume"), "default": 100}
            ]},
            {"label": "Telegram Config", "fields": [
                {"name": "telegram_bot_token", "type": "text", "label": self._("Enter a telegram bot token, Optional: "), "default": ""},
            ]},
            {"label": "Exclusion Config", "fields": [
                {"name": "exclusion_ips", "type": "text", "label": self._("Exclusion IPs (comma-separated)"), "default": "139.144.24.23"},
                {"name": "exclusion_usernames", "type": "text", "label": self._("Exclusion Usernames (comma-separated)"), "default": ""},
                {"name": "exclusion_nicknames", "type": "text", "label": self._("Exclusion Nicknames (comma-separated)"), "default": ""},
            ]},
            {"label": "Weather Config", "fields": [
                {"name": "weather_api_key", "type": "text", "label": self._("Weather API Key"), "default": "33cd6adaa1914163b5f84718242103"},
            ]},
            {"label": "SSH Config", "fields": [
                {"name": "ssh_hostname", "type": "text", "label": self._("SSH Hostname"), "default": ""},
                {"name": "ssh_port", "type": "int", "label": self._("SSH Port"), "default": 22},
                {"name": "ssh_username", "type": "text", "label": self._("SSH Username"), "default": ""},
                {"name": "ssh_password", "type": "password", "label": self._("SSH Password"), "default": ""},
                {"name": "allowed_ips", "type": "text", "label": self._("List of allowed IPs to execute ssh commands: "), "default": ""},
            ]},
            {"label": "Accounts Config", "fields": [
                {"name": "accounts_detection_mode", "type": "radio", "label": self._("Detection Mode"), "options": [self._("Guest Accounts"), self._("All Accounts"), self._("Custom Username Account")], "default": self._("Guest Accounts")},
                {"name": "accounts_custom_username", "type": "text", "label": self._("Custom Username"), "default": "", "hint": self._("This field is only required if 'Custom Username Account' is selected above.")},
                {"name": "accounts_authorized_users", "type": "text", "label": self._("Authorized Usernames (comma-separated)"), "default": ""},
                {"name": "detect_server_admins", "type": "bool", "label": self._("Detect server administrators as bot's authorized users"), "default": False}
            ]},
            {"label": "Teamtalk license", "fields": [
                {"name": "license_name", "type": "text", "label": self._("License name"), "default": ""},
                {"name": "license_key", "type": "text", "label": self._("License key"), "default": ""}
            ]}
        ]

        self.values = {}
        self.panel = None

        # Initialize UI with default language first
        self.InitUI()


    def InitUI(self):
        # Translation - update dynamically based on self.language
        gettext.bindtextdomain("messages", "locales")
        gettext.textdomain("messages")  
        try:
            translation = gettext.translation("messages", "locales", [self.language])
            translation.install()
            self._ = translation.gettext
        except FileNotFoundError:
            print(f"Language '{self.language}' not found, defaulting to English.")

        if self.panel:
            # Get the current sizer and replace it later
            sizer = self.panel.GetSizer()
            self.panel.DestroyChildren()
            self.panel.ClearBackground()

        else:
            self.panel = wx.Panel(self)
            sizer = wx.BoxSizer(wx.VERTICAL)
            self.panel.SetSizer(sizer)


        self.section_label = wx.StaticText(self.panel, label=self.sections[self.current_section]["label"])
        self.fields_sizer = wx.BoxSizer(wx.VERTICAL)
        self.create_fields(self.panel) # Create initial fields

        self.back_button = wx.Button(self.panel, label=self._("Back"))
        self.back_button.Hide() 
        self.next_button = wx.Button(self.panel, label=self._("Next"))

        self.save_button = wx.Button(self.panel, label=self._("Save"))
        self.save_button.Hide()

        self.list_label = wx.StaticText(self.panel, label=self._("Review your configuration settings. Press finish to confirm"))
        self.list_box = wx.ListBox(self.panel, choices=[], style=wx.LB_SINGLE)
        self.list_box.Hide()
        self.list_label.Hide()

        self.finish_button = wx.Button(self.panel, label=self._("Finish"))
        self.finish_button.Hide()

        sizer.Add(self.section_label, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        sizer.Add(self.fields_sizer, 1, wx.EXPAND | wx.ALL, border=5)
        sizer.Add(self.back_button, flag=wx.ALIGN_LEFT | wx.ALL, border=5)
        sizer.Add(self.next_button, flag=wx.ALIGN_RIGHT | wx.ALL, border=5)
        sizer.Add(self.save_button, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        sizer.Add(self.list_label, flag=wx.ALIGN_LEFT | wx.ALL, border=5)
        sizer.Add(self.list_box, flag=wx.EXPAND | wx.ALL, border=5)
        sizer.Add(self.finish_button, flag=wx.ALIGN_CENTER | wx.ALL, border=5)

        self.panel.SetSizer(sizer)

        self.back_button.Bind(wx.EVT_BUTTON, lambda event: self.on_back(event, self.panel))
        self.next_button.Bind(wx.EVT_BUTTON, lambda event: self.on_next(event, self.panel))
        self.save_button.Bind(wx.EVT_BUTTON, self.on_save)
        self.finish_button.Bind(wx.EVT_BUTTON, self.on_finish)

        self.Fit()
        self.SetMinSize((600, 400))
        self.Centre()
        self.Show()


    def create_fields(self, panel):
        self.fields_sizer.Clear(True)
        section = self.sections[self.current_section]
        for field in section["fields"]:
            self.create_field(field, panel)
        self.panel.Layout()
        self.panel.Refresh() # Ensure immediate redraw

    def create_field(self, field, panel):
        field_panel = wx.Panel(panel)
        field_sizer = wx.BoxSizer(wx.HORIZONTAL)

        label = wx.StaticText(field_panel, label=self._(field["label"]))
        field_sizer.Add(label, flag=wx.ALIGN_LEFT | wx.ALL, border=5)

        if field["type"] == "text":
            input_control = wx.TextCtrl(field_panel, value=field["default"])
        elif field["type"] == "int":
            input_control = wx.TextCtrl(field_panel, value=str(field["default"]))
        elif field["type"] == "password":
            input_control = wx.TextCtrl(field_panel, value=field["default"], style=wx.TE_PASSWORD)
        elif field["type"] == "bool":
            input_control = wx.CheckBox(field_panel, label=self._(field["label"]))
            input_control.SetValue(field["default"])
        elif field["type"] == "radio":
            translated_options = [self._(option) for option in field["options"]] # Translate each option
            input_control = wx.RadioBox(field_panel, label=self._(field["label"]), choices=translated_options,
                                       majorDimension=1, style=wx.RA_SPECIFY_COLS)
            try:
                default_index = translated_options.index(self._(field["default"]))
                input_control.SetSelection(default_index)
            except ValueError:
                input_control.SetSelection(0)
        elif field["type"] == "input_device":
            input_control = wx.ComboBox(field_panel, choices=[], style=wx.CB_READONLY)
            self.populate_audio_devices(input_control, teamtalk.SoundDevice.nMaxInputChannels)
            field_id = wx.NewIdRef()
            field["id"] = field_id
            input_control.SetId(field_id)
        elif field["type"] == "output_device":
            input_control = wx.ComboBox(field_panel, choices=[], style=wx.CB_READONLY)
            self.populate_mpv_output_devices(input_control)
            field_id = wx.NewIdRef()
            field["id"] = field_id
            input_control.SetId(field_id)
        elif field["type"] == "language":
            input_control = wx.ComboBox(field_panel, choices=[], style=wx.CB_READONLY)
            self.populate_languages(input_control)
            field_id = wx.NewIdRef()  # Assign ID for language combo box
            field["id"] = field_id
            input_control.SetId(field_id)

            if field["name"] == "accounts_detection_mode":
                self.accounts_detection_mode = input_control
        else:
            print("Error: Unknown field type:", field["type"])
            return

        # Add an ID only if it's an interactive control 
        if field["type"] in ("text", "int", "password", "bool", "radio"): 
            field_id = wx.NewIdRef()
            field["id"] = field_id
            input_control.SetId(field_id)

        field_sizer.Add(input_control, flag=wx.EXPAND | wx.ALL, border=5)

        if field["name"] == "weather_api_key":
            weather_button = wx.Button(field_panel, label=self._("Visit the website to Get a weather API key"))
            weather_button.Bind(wx.EVT_BUTTON, self.on_open_weather_api)
            field_sizer.Add(weather_button, flag=wx.ALL, border=5)

        field_panel.SetSizer(field_sizer)
        self.fields_sizer.Add(field_panel, flag=wx.EXPAND | wx.ALL, border=5)

    def populate_audio_devices(self, combo_box, channel_type):
        """Populates the combo box with audio device names."""
        tt = teamtalk.TeamTalk()
        devices = tt.getSoundDevices()
        for device in devices:
            if channel_type == teamtalk.SoundDevice.nMaxInputChannels:
                channel_name = "nMaxInputChannels"
            else:
                channel_name = "nMaxOutputChannels"
            if getattr(device, channel_name) > 0:
                combo_box.Append(teamtalk.ttstr(device.szDeviceName), device.nDeviceID) 
        tt.closeTeamTalk()
        combo_box.SetSelection(0)

    def populate_mpv_output_devices(self, combo_box):
        player = mpv.MPV()
        for i, device in enumerate(player.audio_device_list):
            combo_box.Append(device['description'], i)
        player.terminate()
        combo_box.SetSelection(0)

    def populate_languages(self, combo_box):
        """Populates the combo box with available languages from the locales directory."""
        locales_dir = "locales"
        if os.path.exists(locales_dir) and os.path.isdir(locales_dir):
            languages = [lang for lang in os.listdir(locales_dir) if os.path.isdir(os.path.join(locales_dir, lang))]
            for lang in languages:
                combo_box.Append(lang, lang)  # Store language code as client data
            combo_box.SetSelection(0)
 
    def on_open_weather_api(self, event):
        webbrowser.open_new_tab("https://www.weatherapi.com/signup.aspx")

    def on_back(self, event, panel):
        self.get_field_values()
        self.current_section = (self.current_section - 1) % len(self.sections)
        self.section_label.SetLabel(self.sections[self.current_section]["label"])
        self.create_fields(panel)
        self.fields_sizer.Layout()
        self.Fit()

        if self.current_section == 0: 
            self.back_button.Hide()

        if self.current_section == len(self.sections) - 1:
            self.save_button.Show()
            self.next_button.Hide()
        else:
            self.save_button.Hide()
            self.next_button.Show()

    def on_next(self, event, panel):
        self.get_field_values()

        if self.current_section == 0:
            lang = self.values.get("language")
            if lang:
                self.language = lang
                self.InitUI()  # Recreate the UI
                self.panel.Layout()

        self.current_section = (self.current_section + 1) % len(self.sections)
        self.section_label.SetLabel(self._(self.sections[self.current_section]["label"]))
        self.create_fields(self.panel)
        self.panel.Layout()
        self.fields_sizer.Layout()
        self.Fit()

        if self.current_section != 0: 
            self.back_button.Show()

        if self.current_section == len(self.sections) - 1:
            self.save_button.Show()
            self.next_button.Hide()
        else:
            self.save_button.Hide()
            self.next_button.Show()

    def on_finish(self, event):
        self.save_config()
        self.Close()

    def on_save(self, event):
        self.get_field_values()

        self.section_label.Hide()
        self.fields_sizer.ShowItems(False)
        self.back_button.Hide()
        self.next_button.Hide()
        self.save_button.Hide()

        self.list_label.Show()
        self.list_box.Show()
        self.finish_button.Show()

        self.list_box.Clear()
        for section in self.sections:
            for field in section["fields"]:
                if "id" in field:
                    value = self.values.get(field["name"])
                    if value is not None:
                        self.list_box.Append(f"{field['label']}: {value}")


    def on_finish(self, event):
        self.save_config()
        self.Close()

    def get_field_values(self):
        section = self.sections[self.current_section]
        for field in section["fields"]:
            if "id" in field: 
                control = self.FindWindowById(field["id"])
                if control:
                    if field["type"] == "bool":
                        self.values[field["name"]] = control.GetValue()
                    elif field["type"] == "radio":
                        self.values[field["name"]] = control.GetStringSelection()
                    elif field["type"] == "int":
                        try:
                            self.values[field["name"]] = int(control.GetValue())
                        except ValueError:
                            print(f"Error: Invalid integer value for {field['name']}")
                            self.values[field["name"]] = field["default"]
                    elif field["type"] in ("input_device", "output_device"):
                        try:
                            self.values[field["name"]] = control.GetClientData(control.GetSelection()) 
                        except ValueError:
                            print(f"Error: Invalid value for {field['name']}")
                            self.values[field["name"]] = field["default"]
                    else:
                        self.values[field["name"]] = control.GetValue()

    def save_config(self):
        config = configparser.ConfigParser()

        def get_replaced_value(field_name, value):
            if field_name == "blacklist_mode":
                return "1" if value == self._("Kick the user") else "2" 
            elif field_name == "char_limit_mode":
                return "1" if value == self._("Kick the user") else "2"
            elif field_name == "bot_gender":
                if value == self._("Male"):
                    return "0"
                elif value == self._("Female"):
                    return "256"
                elif value == self._("Neutral"):
                    return "4096"
            elif field_name == "accounts_detection_mode":
                if value == self._("Guest Accounts"):
                    return "1"
                elif value == self._("All Accounts"):
                    return "2"
                elif value == self._("Custom Username Account"):
                    return "3"
            else:
                return value

        config["server"] = {
            "address": str(self.values.get("server_address")),
            "port": str(self.values.get("server_port")),
            "encrypted": str(self.values.get("server_encrypted")),
            "username": str(self.values.get("server_username")),
            "password": str(self.values.get("server_password"))
        }
        config["bot"] = {
            "nickname": str(self.values.get("bot_nickname")),
            "client_name": str(self.values.get("bot_client_name")),
            "gender": get_replaced_value("bot_gender", self.values.get("bot_gender")),
            "language": str(self.values.get("language")),
            "default_channel": str(self.values.get("default_channel")),
            "channel_password": str(self.values.get("channel_password")),
            "status_message": str(self.values.get("bot_status_message")),
            "vpn_detection": str(self.values.get("vpn_detection")),
            "prevent_noname": str(self.values.get("prevent_noname")),
            "noname_note": str(self.values.get("noname_note")),
            "intercept_channel_messages": str(self.values.get("intercept_channel_messages")),
            "jail_users": str(self.values.get("jail_users")),
            "jail_names": str(self.values.get("jail_names")),
            "jail_channel": str(self.values.get("jail_channel")),
            "jail_timer_seconds": str(self.values.get("jail_timer_seconds")),
            "jail_flood_count": str(self.values.get("jail_flood_count")),
            "random_message_interval": str(self.values.get("random_message_interval")),
            "char_limit": str(self.values.get("char_limit")),
            "char_limit_mode": get_replaced_value("char_limit_mode", self.values.get("char_limit_mode")),
            "blacklist_mode": get_replaced_value("blacklist_mode", self.values.get("blacklist_mode")),
            "video_deletion_timer": str(self.values.get("video_deletion_timer")),
            "banned_countries": str(self.values.get("banned_countries")),
        }
        config["playback"]= {
            "input_device": str(self.values.get("input_device_id")),
            "output_device": str(self.values.get("output_device_id")),
            "seek_step": str(self.values.get("seek_step")),
            "default_volume": str(self.values.get("default_volume")),
            "max_volume": str(self.values.get("max_volume")),
        }
        config["telegram"] = {
            "telegram_bot_token": str(self.values.get("telegram_bot_token")),
        }
        config["exclusion"] = {
            "ips": str(self.values.get("exclusion_ips")),
            "usernames": str(self.values.get("exclusion_usernames")),
            "nicknames": str(self.values.get("exclusion_nicknames"))
        }
        config["accounts"] = {
            "detection_mode": get_replaced_value("accounts_detection_mode", self.values.get("accounts_detection_mode")), # Replace value
            "custom_username": str(self.values.get("accounts_custom_username")),
            "authorized_users": str(self.values.get("accounts_authorized_users")),
            "detect_server_admins": str(self.values.get("detect_server_admins"))
        }
        config["weather"] = {"api_key": str(self.values.get("weather_api_key"))}
        config["ssh"] = {
            "hostname": str(self.values.get("ssh_hostname")),
            "port": str(self.values.get("ssh_port")),
            "username": str(self.values.get("ssh_username")),
            "password": str(self.values.get("ssh_password")),
            "allowed_ips": str(self.values.get("allowed_ips"))
        }
        config["teamtalk_license"] = {
            "license_name": str(self.values.get("license_name")),
            "license_key": str(self.values.get("license_key")),
        }

        with open("config.ini", "w") as configfile:
            config.write(configfile)
        wx.MessageBox(self._("Congratulations. The config file  has been created successfully. Please run the bot again!."), self._("You're all done."), wx.OK | wx.ICON_INFORMATION)