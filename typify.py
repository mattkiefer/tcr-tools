import parsedatetime
from time import mktime
from datetime import date
from datetime import datetime


def parse_str_date(string,time=False,today_ok=False):
    """ 
    make a date out of
    string using parsedatetime lib,
    return for import
    https://pypi.python.org/pypi/parsedatetime/
    """
    if string:
        try:
            if time:
                the_date = datetime.fromtimestamp(mktime(parsedatetime.Calendar().parse(string)[0]))
            else:
                the_date = date.fromtimestamp(mktime(parsedatetime.Calendar().parse(string)[0]))
            # a little sloppy
            if the_date != date.today() or today_ok or (time and the_date.date == date.today()):
                # this is to avoid the bug where parsedatetime (I think)
                # returns today's date when it fails to find a date
                return the_date
        except:
            return None


def datify(date_str):
    if date_str: 
        date_obj = parse_str_date(date_str)
        month = date_obj.strftime('%b') + ' '
        day = str(int(date_obj.strftime('%d'))) + ', '
        year = date_obj.strftime('%Y')
        return month + day + year


def intify(string):
    if not string:
        return None
    try:
        return int(string)
    except:
        return int(float(string))
    else:
        return None


def floatify(string):
    if not string:
        return None
    if string == 'NA':
        return 0
    try:
        return float(string)
    except:
        return None

