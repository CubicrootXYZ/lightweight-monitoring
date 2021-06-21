# Lightweight Monitoring

Lightweight monitoring tool for pinging hosts. It is no fully featured monitoring tool - and not meant so. 

This tool is desired for having a simple way to monitor your monitoring. Point it at your monitoring host and you will get notified as soon as it dies.

## Mailing 

### Alerting

Alerts are send as soon as the host is down for 2 request intervals. If the host stays down you will receive an alert each `alert_distance` minutes.

E.g. if your `request_interval` time is 5 minutes and alert will be send 10 minutes after the host went down. If your `alert_distance` is 60 minutes, you will receive a mail each 60 minutes until your host is back up again.

### Resolving

Resolves are send after 2 sucessful intervals. 

## Execution

Copy `config.example.yml` to `config.yml` and adapt the settings.

```
python3 monitoring.py
```