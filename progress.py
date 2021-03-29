import sys, time

def print_progress(count,length):
    sys.stdout.write('\r' + str(count) + '/' + str(length))
    sys.stdout.flush()
