import os
import sys
import time
import smtplib
import getpass
import socket
import argparse
from email.mime.text import MIMEText


def check_pid(pid):
    """
    Check For the existence of a unix pid.

    See: http://stackoverflow.com/questions/568271/check-if-pid-is-not-in-use-in-python
    """

    try:
        os.kill(pid, 0)
    except OSError:
        return False
    else:
        return True


def wait_for_pid(pid):
    """
    Wait for process (pid) to complete before returning.
    """

    t0 = time.time()
    while check_pid(pid):
        print "\rWaiting for pid %d to complete. (%d s)..." % (pid, time.time()-t0),
        sys.stdout.flush()
        time.sleep(1)
    print "\nDone!"


def notify(pid, recipients, name=None, sender=None):
    """
    Send email notification to list of recipients, regarding
    process (pid) completing.
    """

    recipients = recipients if type(recipients) in [list, tuple] else [recipients]
    name = name or "Your process"
    sender = sender or getpass.getuser() + "@" + socket.gethostname()
    text = "%s (pid %s), finished running." % (name, pid)

    msg = MIMEText(text)
    msg['Subject'] = text
    msg['From'] = sender
    msg['To'] = ", ".join(recipients)

    s = smtplib.SMTP('127.0.0.1')
    s.sendmail(sender, recipients, msg.as_string())
    s.quit()
    print "Sent email notification to %s." % (msg['To'])


if __name__ == "__main__":
    """
    Parse arguments, wait, then notify.
    """

    parser = argparse.ArgumentParser(description='Process some integers.')

    parser.add_argument('pid', type=int,
                        help='a process id number to watch')
    parser.add_argument('-e', '--email', required=True, type=str,
                        help='email address to send notification')
    parser.add_argument('-n', '--name', type=str, default=None,
                        help='human-readable name to give the process')
    parser.add_argument('-s', '--sender', type=str, default=None,
                        help='email address to send email from')

    args = parser.parse_args()

    if check_pid(args.pid):
        wait_for_pid(args.pid)

        notify(args.pid,
               [s.strip() for s in args.email.split(',')],
               name=args.name,
               sender=args.sender)

    else:
        print "Process id %d does not appear to be running." % args.pid
