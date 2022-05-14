from flask import redirect, request, url_for

# Redirect to the endpoint in the 'next' parameter
# if it exists and is valid, else redirect to a fallback
def url_destination(fallback):
	dest = request.args.get('next')
	try:
		url_dest = url_for(dest)
	except:
		return redirect(fallback)
	return redirect(url_dest)