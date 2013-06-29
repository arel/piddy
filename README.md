piddy
=====

A lightweight email notifier for long-running processes.

Given a process specified by its ID number (e.g., as found by `ps -fe` or `top`),
piddy waits for the process to finish, and then sends an email notification to one or more
people.

### requirements
  * `sendmail` is required on localhost to send email (or any SMTP mail server compatible with Python's built-in `smtplib`).
  * alternatively you can use another SMTP server like Gmail, by using the `-p` flag.

### examples

Find the process id using a command like `ps`.
```
(env)Daenerys:pid-note iqe$ ps -fe | grep python
  501 30406 29915   0 11:28PM ttys001    0:00.00 grep python
  501 30119 30114   0  8:24PM ttys002    0:00.06 /usr/local/Cellar/python/2.7.3/Frameworks/Python.framework/Versions/2.7/Resources/Python.app/Contents/MacOS/Python longComputation.py
```

In this case, let's listen for my Python process (30119). To schedule a notification when the process finishes:
```
$ python piddy.py -e arel@example.com 30119

Waiting for pid 30119 to complete. (10 s)...
Done!
Sent email notification to arel@example.com.
```

You can send to multiple email addresses by separating them with commas.

### usage

```
usage: piddy.py [-h] -e EMAIL [-n NAME] [-s SENDER] pid

Notify by email when a process finishes running. Given a process specified by
its ID number (e.g., as found by "ps -fe" or "top"), wait for the process to
finish, and send an email notification to one or more people. Email is sent
via smtplib. REQUIRES sendmail to be installed.

positional arguments:
  pid                   a process id number to watch

optional arguments:
  -h, --help            show this help message and exit
  -e EMAIL, --email EMAIL
                        email address to send notification (comma-separated if
                        more than one recipient)
  -n NAME, --name NAME  human-readable name to give the process
  -s SENDER, --sender SENDER
                        email address to send email from
  -p, --prompt          prompt for SMTP credentials
```
