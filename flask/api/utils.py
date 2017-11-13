from random import SystemRandom
import string

def random_sleep_time(lower_bound=10, upper_bound=30, factor=10.0):
	#with a CSPRNG, get a value between 10 and 30
	r = SystemRandom().randint(lower_bound, upper_bound)

	#divide so we get a value between 1 and 3 seconds
	return float(r/factor)

def flip_coin(weight=.5):
	#with a CSPRNG, get a value between 10 and 30
	r = SystemRandom().random()

	return r >= weight

def random_data(size=35):
	# return a random string. stolen from: https://stackoverflow.com/a/2257449/1200388
	return ''.join(SystemRandom().choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for _ in xrange(size))

def random_username():
	users = [
		"admin",
		"dev-reader",
		"dev-writer",
		"test",
		"user",
		"poweruser"
	]

	#similar to random_data(). return a random username from users list
	return ''.join(SystemRandom().choice(users) for _ in xrange(1))
