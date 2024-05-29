import sys
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio
import os, datetime,threading,time,zoneinfo,re,tzlocal,calendar,subprocess
from preferences import Preferences

class MyApp(Adw.Application):
    stop_event = threading.Event()
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect('activate', self.on_activate)
        self.builder = Gtk.Builder()
        self.builder.add_from_file("UI/example.ui")
        self.apply = self.builder.get_object("apply")
        self.hours = self.builder.get_object("hours")
        self.minutes = self.builder.get_object('minutes')
        self.seconds = self.builder.get_object('seconds')
        self.timezone = self.builder.get_object('timezone')
        self.calendar = self.builder.get_object('Calendar')
        self.thread = threading.Thread(target=self.set_dropdowntime)
        #radio button init
        self.autotime = self.builder.get_object('autotime')
        self.autotime.connect("toggled", self.Automatically_Time_Handler)
        if subprocess.run(["timedatectl show | grep -oP '^NTP=\K.*'"], shell=True, capture_output=True, text=True).stdout.strip() == "yes":
            self.autotime.set_active(True)
        else:
            self.autotime.set_active(False)
        if self.autotime.get_active() == True:
            self.Automatically_Time_Handler(self)

        #apply button connect
        self.apply.connect("clicked", self.apply_handler)
        #menubar init
        action_map = {
            "app.preferences": self.on_preferences,
            "app.about": self.on_about,
        }

        for action_name, action_callback in action_map.items():
            action = Gio.SimpleAction.new(action_name.split('.')[1], None)
            action.connect("activate", action_callback)
            self.add_action(action)
        #set stringlist model
        self.hours_gstringlist = Gtk.StringList()
        self.minutes_gstringlist = Gtk.StringList()
        self.seconds_gstringlist = Gtk.StringList()
        self.tz_gstringlist = Gtk.StringList()
        self.tz_gstringlist.append(str(tzlocal.get_localzone()))
        for i in self.tz_sortedlist():
            self.tz_gstringlist.append(i)
        for i in range(24):
            if i <= 9:
                self.hours_gstringlist.append("0" + str(i))
            else:
                self.hours_gstringlist.append(str(i))
        for i in range(60):
            if i <= 9:
                self.minutes_gstringlist.append("0" + str(i))
                self.seconds_gstringlist.append("0" + str(i))
            else:
                self.minutes_gstringlist.append(str(i))
                self.seconds_gstringlist.append(str(i))
        self.hours.set_model(self.hours_gstringlist)
        self.minutes.set_model(self.minutes_gstringlist)
        self.seconds.set_model(self.seconds_gstringlist)
        self.timezone.set_model(self.tz_gstringlist)
        #dropdown realtime
        self.hours.set_selected(datetime.datetime.now().hour)
        self.minutes.set_selected(datetime.datetime.now().minute)
        self.seconds.set_selected(datetime.datetime.now().second)

        #check priviligies
        if os.geteuid() == 0:
            #kill chronyd
            try:
                if subprocess.run(["cat /etc/systemd/timesyncd.conf | grep -oP '#NTP='"], shell=True, capture_output=True, text=True).stdout.strip() == "#NTP=":
                    subprocess.run(["sed -i 's/#NTP=/NTP=/g' /etc/systemd/timesyncd.conf"], shell = True,executable='/bin/bash')

                if subprocess.run(["cat /etc/systemd/timesyncd.conf | grep -oP '^NTP=\K.*'"], shell=True, capture_output=True, text=True).stdout.strip() == "":
                    subprocess.run(["sed -i 's/^NTP=$/NTP=ntp0.vniiftri.ru ntp1.vniiftri.ru ntp2.vniiftri.ru ntp3.vniiftri.ru/' /etc/systemd/timesyncd.conf"], shell = True,executable='/bin/bash')
                subprocess.call(["systemctl disable chronyd && systemctl stop chronyd"], shell = True,executable='/bin/bash')
            except:
                pass
        else:
            self.apply.set_sensitive(False)
            self.hours.set_sensitive(False)
            self.minutes.set_sensitive(False)
            self.seconds.set_sensitive(False)
            self.timezone.set_sensitive(False)
            self.calendar.set_sensitive(False)
            self.autotime.set_sensitive(False)

    def on_preferences(self,action, param):
        pref = Preferences(self)
        pref.on_activate()

    def on_about(self,action,param):
        about = Gtk.AboutDialog(transient_for=self.props.active_window,
                        modal=True,
                        program_name='test',
                        logo_icon_name='org.glazov.test',
                        version='0.1.0',
                        authors=['alex'],
                        copyright='© 2024 alex')
        about.present()

    def tz_sortedlist(self):
        tz_list = []
        for i in zoneinfo.available_timezones():
            if i == str(tzlocal.get_localzone()):
                i=""
            elif re.match(r'Asia', i) != None:
                tz_list.append(i)
            elif re.match(r'Europe', i) != None:
                tz_list.append(i)
            elif re.match(r'America', i) != None:
                tz_list.append(i)
            elif re.match(r'Africa', i) != None:
                tz_list.append(i)
            elif re.match(r'Pacific', i) != None:
                tz_list.append(i)
            elif re.match(r'US', i) != None:
                tz_list.append(i)
            elif re.match(r'Atlantic', i) != None:
                tz_list.append(i)
            elif re.match(r'Australia', i) != None:
                tz_list.append(i)
            elif re.match(r'Brazil', i) != None:
                tz_list.append(i)
            elif re.match(r'Canada', i) != None:
                tz_list.append(i)
            elif re.match(r'Indian', i) != None:
                tz_list.append(i)
            elif re.match(r'Chile', i) != None:
                tz_list.append(i)
            elif re.match(r'Mexico', i) != None:
                tz_list.append(i)
        return sorted(tz_list)

    def set_dropdowntime(self):
        while True:
            if self.stop_event.is_set() == False:
                self.hours.set_selected(datetime.datetime.now(tzlocal.get_localzone()).hour)
                self.minutes.set_selected(datetime.datetime.now(tzlocal.get_localzone()).minute)
                self.seconds.set_selected(datetime.datetime.now(tzlocal.get_localzone()).second)
            else:
                pass

    def on_activate(self, app):
        self.win = self.builder.get_object("main_window")
        self.win.set_application(self)  # Application will close once it no longer has active windows attached to it
        self.win.present()

    def apply_handler(self, button):
        if os.geteuid() == 0:
            if self.autotime.get_active() == True:
                subprocess.run(["timedatectl set-timezone {}".format(self.tz_gstringlist.get_string(self.timezone.get_selected()))], shell = True,executable='/bin/bash')
            else:
                subprocess.call(["timedatectl -- set-time '{}-{}-{} {}:{}:{}' ".format(self.calendar.get_date().get_year(),self.calendar.get_date().get_month(),self.calendar.get_date().get_day_of_month(), self.hours_gstringlist.get_string(self.hours.get_selected()), self.minutes_gstringlist.get_string(self.minutes.get_selected()), self.seconds_gstringlist.get_string(self.seconds.get_selected()) )], shell = True,executable='/bin/bash')
                subprocess.run(["timedatectl set-timezone {}".format(self.tz_gstringlist.get_string(self.timezone.get_selected()))], shell = True,executable='/bin/bash')
            time.tzset()
            self.hours.set_selected(datetime.datetime.now().hour)
            self.minutes.set_selected(datetime.datetime.now().minute)
            self.seconds.set_selected(datetime.datetime.now().second)
    def Automatically_Time_Handler(self, handler):
        if self.autotime.get_active() == True:
            self.stop_event.clear()
            self.hours.set_sensitive(False)
            self.minutes.set_sensitive(False)
            self.seconds.set_sensitive(False)
            self.calendar.set_sensitive(False)
            time.tzset()
            self.hours.set_selected(datetime.datetime.now().hour)
            self.minutes.set_selected(datetime.datetime.now().minute)
            self.seconds.set_selected(datetime.datetime.now().second)
            if os.geteuid() == 0:
                try:
                    subprocess.run(["systemctl enable systemd-timesyncd && systemctl start systemd-timesyncd && timedatectl set-ntp true"], shell = True,executable='/bin/bash')
                except:
                    pass
        else:
            self.calendar.set_sensitive(True)
            self.hours.set_sensitive(True)
            self.minutes.set_sensitive(True)
            self.seconds.set_sensitive(True)
            self.stop_event.set()
            if os.geteuid() == 0:
                try:
                    subprocess.run(["systemctl disable systemd-timesyncd && systemctl stop systemd-timesyncd && timedatectl set-ntp false"], shell = True,executable='/bin/bash')
                except:
                    pass


app = MyApp(application_id="com.glazov.test")
app.run(sys.argv)
