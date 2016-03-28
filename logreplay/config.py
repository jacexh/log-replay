class config(object):

    REPEATER_NUMBER = 2
    PLAYER_NUMBER = 4
    THREAD_POOL_NUMBER = 5
    GATHER_INTERVAL = 10
    RESPONSE_HANDLER = lambda p: print(p.result())
