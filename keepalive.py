"""
Pings os.environ["HOSTNAME"] to keep dyno alive.
"""
import os
import urllib2


def keep_alive():
    hostname = os.environ.get("HOSTNAME")
    if hostname:
        print('ping "%s"' % hostname)
        url = "http://" + hostname
        urllib2.urlopen(url)
    else:
        print("Couldn't keep alive, HOSTNAME not set")

if __name__ == "__main__":
    keep_alive()
