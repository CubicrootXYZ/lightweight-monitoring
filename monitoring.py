import subprocess as sp
import yaml
import time
import datetime
import smtplib


class Config:
    hosts = []
    requestIntervalMinutes = 0
    mail = {}
    debug = False
    alertDistance = 60

    # read reads the config file
    def read(self):
        # Read YAML file
        with open("config.yml", 'r') as stream:
            data_loaded = yaml.safe_load(stream)

        if 'hosts' in data_loaded and type(data_loaded['hosts']) is list:
            self.hosts = data_loaded['hosts']
        else:
            raise ValueError("Failed parsing config.yml, missing 'hosts'")

        if 'alert_distance' in data_loaded and type(data_loaded['alert_distance']) is int:
            self.alertDistance = data_loaded['alert_distance']
        else:
            raise ValueError(
                "Failed parsing config.yml, missing 'alert_distance'")

        if 'request_interval' in data_loaded and type(data_loaded['request_interval']) is int:
            self.requestIntervalMinutes = data_loaded['request_interval']
        else:
            raise ValueError(
                "Failed parsing config.yml, missing 'request_interval'")

        if 'mail' in data_loaded and type(data_loaded['mail']) == dict:
            for key in ['server', 'port', 'username', 'password', 'from', 'to']:
                if key not in data_loaded['mail']:
                    raise ValueError(
                        f"Failed parsing config.yml, missing 'mail.{key}'")

            self.mail = data_loaded['mail']
        else:
            raise ValueError("Failed parsing config.yml, missing 'mail'")

        if 'debug' in data_loaded and type(data_loaded['debug']) is bool:
            self.debug = data_loaded['debug']


class Monitor:
    lastRun = {}
    thisRun = {}
    alerts = {}

    def __init__(self, config):
        self.config = config

    # run runs monitoring in a loop
    def run(self):
        while True:
            print(
                "INFO: Checking hosts at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
            for host in self.config.hosts:
                status, _ = sp.getstatusoutput("ping -c1 -w2 " + host)

                if status != 0:
                    print(f"INFO: Host {host} is DOWN!")
                    self.alert(host)
                else:
                    self.resolve(host)

                self.thisRun[host] = status == 0

            self.lastRun = self.thisRun
            self.thisRun = {}

            if self.config.debug:
                time.sleep(5)
            else:
                time.sleep(self.config.requestIntervalMinutes*60)

    # alert is called when a host is offline
    def alert(self, host):
        # First alert after init
        if host not in self.lastRun:
            return

        # Already alerted
        if host in self.alerts and self.alerts[host] > datetime.datetime.now() - datetime.timedelta(minutes=self.config.alertDistance):
            return

        # First alert, wait for second in a row
        if self.lastRun[host] == True:
            return

        print(f"INFO: Sending alert for host {host}")
        if self.send_mail(
            f"Host {host} not reachable - {datetime.datetime.now().strftime('%d.%m %H:%M')}",
            f"Host {host} not reachable - {datetime.datetime.now().strftime('%H:%M %Y-%m-%d')}"
        ):
            self.alerts[host] = datetime.datetime.now()

    # resolve is called when a host is online
    def resolve(self, host):
        # First alert after init or no alert open
        if host not in self.lastRun or host not in self.alerts:
            return

        # Resolve after 2 intervals
        if self.lastRun[host] == False:
            return

        print(f"INFO: Sending resolve for host {host}")
        if self.send_mail(
            f"[RESOLVED] Host {host} reachable again - {datetime.datetime.now().strftime('%d.%m %H:%M')}",
            f"[RESOLVED] Host {host} reachable again - {datetime.datetime.now().strftime('%H:%M %Y-%m-%d')}"
        ):
            del self.alerts[host]

    # send_mail sends a mail
    def send_mail(self, subject, message):
        try:
            msg = f"Subject: {subject}\n\n{message}"

            # Login and send mail
            server = smtplib.SMTP(
                self.config.mail['server'], self.config.mail['port'])
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(self.config.mail['username'],
                         self.config.mail['password'])
            server.sendmail(self.config.mail['from'],
                            self.config.mail['to'], msg)
            server.quit()
        except Exception as e:
            print(
                f"ERROR: Mail sending failed (server: {self.config.mail['server']}, port:{self.config.mail['port']} , username: {self.config.mail['username']}): {e}")
            return False

        return True


c = Config()
c.read()

r = Monitor(c)
r.run()
