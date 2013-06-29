piddy
=====

A lightweight email notifier for long-running processes.

Given a process specified by its ID number (e.g., as found by `ps -fe` or `top`),
piddy waits for the process to finish, and then sends an email notification to one or more
people.

### requirements
Either:
  * an SMTP server such as `sendmail` running on localhost
  * or credentials to an external SMTP server, such as Gmail (see the `-p` or `-g` flags).

### examples

Find the process id using a command like `ps`.
```
$ ps -fe | grep python
  501 30406 29915   0 11:28PM ttys001    0:00.00 grep python
  501 30119 30114   0  8:24PM ttys002    0:00.06 Python longComputation.py
```

In this case, let's listen for my Python process (30119) to finish. To schedule a notification when the process finishes:
```
$ python piddy.py -e arel@example.com 30119

Waiting for pid 30119 to complete. (10 s)...
Done!
Sent email notification to arel@example.com.
```

If we don't have `sendmail` running locally, we can enter our credentials
for an external server:
```
$ python piddy.py -e arel@example.com --gmail 30119

What is your SMTP user name (e.g., your email address)?
Username (arel@example.com):
Password:
SMTP host name (smtp.gmail.com):
Credentials accepted.
Waiting for pid 30119 to complete. (44 s)...
Done!
Sent email notification to arel@example.com.
```

You can also send a notification to multiple email addresses by separating them with commas.

### usage

```
usage: piddy.py [-h] -e EMAIL [-n NAME] [-s SENDER] [-p] [-g] pid

Notify by email when a process finishes running. Given a process specified by
its ID number (e.g., as found by "ps -fe" or "top"), wait for the process to
finish, and send an email notification to one or more people. Email is sent
via smtplib. REQUIRES either an SMTP server running on localhost, or correct
credentials to an external SMTP server such as a Gmail account.

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
  -g, --gmail           prompt for Gmail credentials (implies -p)
```
