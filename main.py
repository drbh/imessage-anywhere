from threading import Timer
import os
import sys
import sqlite3
import datetime


USERNAME = os.popen('whoami').read().strip()

class ImessageRubyWrapper(object):
    """docstring for ClassName"""
    def __init__(self):
        self.base = "imessage"

    def _set_text(self, text):
        self.text =  '--text ' + '"' + text + '"'

    def _set_contact(self, contact):
        self.contact = '--contacts ' + '"' + contact + '"'

    def command(self, text, contact):
        self._set_text(text)
        self._set_contact(contact)
        cmd = ' '.join([self.base,self.text,self.contact])
        print cmd
        os.system(cmd)


class DataGrabber(object):
    """docstring for ClassName"""
    def __init__(self):
        print '/Users/'+USERNAME+'/Library/Messages/chat.db'
        self.conn = sqlite3.connect('/Users/'+USERNAME+'/Library/Messages/chat.db', check_same_thread=False)
        self.OSX_EPOCH = 978307200
        
    def get_table_names(self):
        c = self.conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table';")
        print(c.fetchall())

    def get_messages(self, handle_id):
        c = self.conn.cursor()
        c.execute("SELECT * FROM `message` WHERE handle_id=" + str(handle_id) + " ORDER BY date DESC LIMIT 20" )
        all_messages = c.fetchall()[::-1]
        payload = []
        for message in all_messages:
            fro = "ME" if message[21] == 1 else "THEM"
            payload += [ { "message":message[2], "time":str(datetime.datetime.fromtimestamp(message[15] + self.OSX_EPOCH)), "from":fro } ]
        c.close()
        return payload

    def get_handles_like(self, search):
        c = self.conn.cursor()
        c.execute("SELECT * FROM `handle` WHERE id LIKE '%"+search+"%'")
        all_handles = c.fetchall()
        c.close()
        return all_handles

    def get_all_conversations(self, handle_id):
        c = self.conn.cursor()
        c.execute("SELECT * FROM `chat_handle_join` WHERE handle_id=" + str(handle_id))
        all_convs = c.fetchall()
        c.close()
        return all_convs

    def find_get_messages(self, search):
        payload = []
        for hand in self.get_handles_like(search):
            # print hand
            payload += [self.get_messages(hand[0])]
        return payload


class DataPoller(object):
    """docstring for ClassName"""
    def __init__(self, conn):
        self.con = conn
        self.last_recorded = 0
        
    def get_last_message_time(self):
        c = self.con.cursor()
        c.execute("select date from message ORDER BY date DESC LIMIT 1")
        last_message_time = c.fetchone()[0]
        return last_message_time
        
    def check_new_message(self):
        most_recent = self.get_last_message_time()
        if most_recent > self.last_recorded:
            self.last_recorded = most_recent
            return True
        return False


class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer     = None
        self.interval   = interval
        self.function   = function
        self.args       = args
        self.kwargs     = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False


