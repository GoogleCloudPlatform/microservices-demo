from time import sleep


def run_poor_implementation():
    lens =  10000
    accu = 0
    for i in range(lens):
        # Something large and take time
        sleep(1)
        accu += 1
    return accu