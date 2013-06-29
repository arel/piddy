import os
import sys
import time
import smtplib
import getpass
import socket
import argparse
from email.mime.text import MIMEText


description = """

Notify by email when a process finishes running.

Given a process specified by its ID number (e.g., as found by "ps -fe" or "top"),
wait for the process to finish, and send an email notification to one or more
people. Email is sent via smtplib.

REQUIRES an SMTP server running either on localhost, or correct credentials to an
external SMTP server such as a Gmail account.

"""


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

    try:
        t0 = time.time()
        while check_pid(pid):
            print "\rWaiting for pid %d to complete. (%d s)..." % (pid, time.time()-t0),
            sys.stdout.flush()
            time.sleep(1)
        print "\nDone!"
    except (KeyboardInterrupt, SystemExit):
        print "\nCanceled."
        sys.exit(2)

def prompt_for_credentials(default_user="", default_host=""):
    """
    Prompts for user credentials for custom SMTP server.
    Assumes TLS, port 587, for now.

    Tests connection and exits if failure.
    """

    print "What is your SMTP user name (e.g., your email address)?"
    user = raw_input("Username (%s): " % default_user).strip() or default_user
    password = getpass.getpass()

    default_host = default_host or ("smtp." + user.split("@", 1)[1] if "@" in user else "")
    host = raw_input("SMTP host name (%s): " % (default_host)) or default_host
    host = host.strip()
    port = 587

    return {"host": host, "port": port, "user": user, "password": password}


def test_credentials(credentials):
    try:
        if credentials:
            # Test external server connection
            s = smtplib.SMTP(credentials["host"], credentials["port"])
            s.ehlo()
            s.starttls()
            s.ehlo()
            result, message = s.login(credentials["user"], credentials["password"])
            s.quit()
            if result != 235:
                print message
                raise
        else:
            # Test local server connection
            s = smtplib.SMTP('127.0.0.1')
            s.quit()

    except smtplib.SMTPException:
        print "Could not authenticate to SMTP server"
        sys.exit(1)
    except smtplib.SMTPHeloError:
        print "There was a problem communicating with the SMTP server."
        sys.exit(1)
    except RuntimeError:
        print "Runtime error. Python does not support SSL/TLS"
        sys.exit(1)
    except:
        host = credentials.get("host") if credentials else "127.0.0.1"
        print "Could not connect to SMTP server (%s)." % host
        sys.exit(1)

    print "Credentials accepted."
    return True


def notify(pid, recipients, name=None, sender=None,
           smtp_credentials=None):
    """
    Send email notification to list of recipients, regarding
    process (pid) completing.
    """

    recipients = recipients if type(recipients) in [list, tuple] else [recipients]
    name = ", " + name if name else ""
    sender = sender or getpass.getuser() + "@" + socket.gethostname()
    text = "Your process%s (pid %s), finished running." % (name, pid)

    msg = MIMEText(text)
    msg['Subject'] = text
    msg['From'] = sender
    msg['To'] = ", ".join(recipients)

    if smtp_credentials == None:
        # Send via localhost SMTP server
        s = smtplib.SMTP('127.0.0.1')
        s.sendmail(sender, recipients, msg.as_string())
        s.quit()
    else:
        # Send via custom server (e.g., gmail)
        # NOTE: TLS is assumed.
        s = smtplib.SMTP(smtp_credentials["host"], smtp_credentials["port"])
        s.ehlo()
        s.starttls()
        s.ehlo()
        s.login(smtp_credentials["user"], smtp_credentials["password"])
        s.sendmail(smtp_credentials["user"], recipients, msg.as_string())
        s.quit()

    print "Sent email notification to %s." % (msg['To'])


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description=description)

    parser.add_argument('pid', type=int,
                        help='a process id number to watch')
    parser.add_argument('-e', '--email', required=True, type=str,
                        help='email address to send notification (comma-separated if more than one recipient)')
    parser.add_argument('-n', '--name', type=str, default=None,
                        help='human-readable name to give the process')
    parser.add_argument('-s', '--sender', type=str, default=None,
                        help='email address to send email from')
    parser.add_argument('-p', '--prompt', action="store_true", default=False,
                        help='prompt for SMTP credentials')
    parser.add_argument('-g', '--gmail', action="store_true", default=False,
                        help='prompt for Gmail credentials (implies -p)')

    # By default, print help and exit
    if len(sys.argv) == 1:
        sys.argv.append("-h")

    args = parser.parse_args()

    if check_pid(args.pid):

        recipients = [s.strip() for s in args.email.split(',')]
        default_user = (args.sender or recipients[0])

        if args.gmail:
            credentials = prompt_for_credentials(default_user, "smtp.gmail.com")
        elif args.prompt:
            credentials = prompt_for_credentials(default_user)
        else:
            credentials = None

        test_credentials(credentials)

        wait_for_pid(args.pid)

        notify(args.pid,
               recipients,
               name=args.name,
               sender=args.sender,
               smtp_credentials=credentials)

    else:
        print "Process id %d does not appear to be running." % args.pid
