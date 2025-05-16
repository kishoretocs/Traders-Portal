from rest_framework.throttling import UserRateThrottle

class WatchlistThrottle(UserRateThrottle):
    rate = '10/hour'