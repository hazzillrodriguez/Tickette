from app.models import Ticket
import random
import string

# Generate random (n) digits for ticket number
def random_numbers():
	number = ''.join(random.SystemRandom().choice(string.digits) for _ in range(8))
	result = Ticket.query.filter_by(number=number).first()
	if result:
		return random_numbers()
	else:
		return number