#!/usr/bin/python3

import os, os.path, re, json, base64

from functools import wraps

from flask import Flask, request, render_template, abort, Response

import auth, utils
from mailconfig import get_mail_users, add_mail_user, set_mail_password, remove_mail_user
from mailconfig import get_mail_user_privileges, add_remove_mail_user_privilege
from mailconfig import get_mail_aliases, get_mail_domains, add_mail_alias, remove_mail_alias

env = utils.load_environment()

auth_service = auth.KeyAuthService()

# We may deploy via a symbolic link, which confuses flask's template finding.
me = __file__
try:
	me = os.readlink(__file__)
except OSError:
	pass

app = Flask(__name__, template_folder=os.path.join(os.path.dirname(me), "templates"))

# Decorator to protect views that require authentication.
def authorized_personnel_only(viewfunc):
	@wraps(viewfunc)
	def newview(*args, **kwargs):
		if not auth_service.is_authenticated(request):
			if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
				# Don't issue a 401 to an AJAX request because the user will
				# be prompted for credentials, which is not helpful.
				abort(403)
			abort(401)
		return viewfunc(*args, **kwargs)
	return newview

@app.errorhandler(401)
def unauthorized(error):
	return auth_service.make_unauthorized_response()

def json_response(data):
	return Response(json.dumps(data), status=200, mimetype='application/json')

###################################

# Control Panel (unauthenticated views)

@app.route('/')
def index():
	# Render the control panel. This route does not require user authentication
	# so it must be safe!
    return render_template('index.html',
    	hostname=env['PRIMARY_HOSTNAME'],
    )

@app.route('/login', methods=['POST'])
def login():
	# Validate the user's credentials and return the daemon's API key
	# (to be used as a shared secret).
	#
	# To avoid CSRF attacks, we do not store user credentials in a cookie.
	# This method is intended to be called via AJAX.
	#
	# This route does not require authentication so it must be safe.

	# Get form fields.
	email = request.form.get('email', '').strip()
	pw = request.form.get('password', '').strip()

	if email == "" or pw == "":
		return json_response({
			"status": "error",
			"message": "Enter an email address and password."
			})

	# Authenticate.
	try:
		# Use doveadm to check credentials. doveadm will return
		# a non-zero exit status if the credentials are no good,
		# and check_call will raise an exception in that case.
		utils.shell('check_call', [
			"/usr/bin/doveadm",
			"auth", "test",
			email, pw
			])
	except:
		# Login failed.
		return json_response({
			"status": "error",
			"message": "Invalid email address or password."
			})

	# Authorize.
	# (This call should never fail on a valid user.)
	privs = get_mail_user_privileges(email, env)
	if isinstance(privs, tuple): raise Exception("Error getting privileges.")
	if "admin" not in privs:
		return json_response({
			"status": "error",
			"message": "You are not an administrator for this system."})

	# User is authenticated & authorized.
	# Provide the user the exact string it should put in the Authorization:
	# header, since it is a little difficult to form in Javascript.
	key = 'Basic ' + base64.b64encode(auth_service.key.encode("ascii") + b':').decode("ascii")
	return json_response({
		"status": "ok",
		"key": key
		})


# MAIL

@app.route('/mail/users')
@authorized_personnel_only
def mail_users():
	if request.args.get("format", "") == "json":
		return json_response(get_mail_users(env, as_json=True))
	else:
		return "".join(x+"\n" for x in get_mail_users(env))

@app.route('/mail/users/add', methods=['POST'])
@authorized_personnel_only
def mail_users_add():
	return add_mail_user(request.form.get('email', ''), request.form.get('password', ''), env)

@app.route('/mail/users/password', methods=['POST'])
@authorized_personnel_only
def mail_users_password():
	return set_mail_password(request.form.get('email', ''), request.form.get('password', ''), env)

@app.route('/mail/users/remove', methods=['POST'])
@authorized_personnel_only
def mail_users_remove():
	return remove_mail_user(request.form.get('email', ''), env)


@app.route('/mail/users/privileges')
@authorized_personnel_only
def mail_user_privs():
	privs = get_mail_user_privileges(request.args.get('email', ''), env)
	if isinstance(privs, tuple): return privs # error
	return "\n".join(privs)

@app.route('/mail/users/privileges/add', methods=['POST'])
@authorized_personnel_only
def mail_user_privs_add():
	return add_remove_mail_user_privilege(request.form.get('email', ''), request.form.get('privilege', ''), "add", env)

@app.route('/mail/users/privileges/remove', methods=['POST'])
@authorized_personnel_only
def mail_user_privs_remove():
	return add_remove_mail_user_privilege(request.form.get('email', ''), request.form.get('privilege', ''), "remove", env)


@app.route('/mail/aliases')
@authorized_personnel_only
def mail_aliases():
    return "".join(x+"\t"+y+"\n" for x, y in get_mail_aliases(env))

@app.route('/mail/aliases/add', methods=['POST'])
@authorized_personnel_only
def mail_aliases_add():
	return add_mail_alias(request.form.get('source', ''), request.form.get('destination', ''), env)

@app.route('/mail/aliases/remove', methods=['POST'])
@authorized_personnel_only
def mail_aliases_remove():
	return remove_mail_alias(request.form.get('source', ''), env)

@app.route('/mail/domains')
@authorized_personnel_only
def mail_domains():
    return "".join(x+"\n" for x in get_mail_domains(env))

# DNS

@app.route('/dns/update', methods=['POST'])
@authorized_personnel_only
def dns_update():
	from dns_update import do_dns_update
	try:
		return do_dns_update(env, force=request.form.get('force', '') == '1')
	except Exception as e:
		return (str(e), 500)

@app.route('/dns/ds')
@authorized_personnel_only
def dns_get_ds_records():
	from dns_update import get_ds_records
	try:
		return get_ds_records(env).replace("\t", " ") # tabs confuse godaddy
	except Exception as e:
		return (str(e), 500)

# WEB

@app.route('/web/update', methods=['POST'])
@authorized_personnel_only
def web_update():
	from web_update import do_web_update
	return do_web_update(env)

# System

@app.route('/system/status', methods=["POST"])
@authorized_personnel_only
def system_status():
	from whats_next import run_checks
	class WebOutput:
		def __init__(self):
			self.items = []
		def add_heading(self, heading):
			self.items.append({ "type": "heading", "text": heading, "extra": [] })
		def print_ok(self, message):
			self.items.append({ "type": "ok", "text": message, "extra": [] })
		def print_error(self, message):
			self.items.append({ "type": "error", "text": message, "extra": [] })
		def print_line(self, message, monospace=False):
			self.items[-1]["extra"].append({ "text": message, "monospace": monospace })
	output = WebOutput()
	run_checks(env, output)
	return json_response(output.items)

@app.route('/system/updates')
@authorized_personnel_only
def show_updates():
	utils.shell("check_call", ["/usr/bin/apt-get", "-qq", "update"])
	simulated_install = utils.shell("check_output", ["/usr/bin/apt-get", "-qq", "-s", "upgrade"])
	pkgs = []
	for line in simulated_install.split('\n'):
		if re.match(r'^Conf .*', line): continue # remove these lines, not informative
		line = re.sub(r'^Inst (.*) \[(.*)\] \((\S*).*', r'Updated Package Available: \1 (\3)', line) # make these lines prettier
		pkgs.append(line)
	return "\n".join(pkgs)

@app.route('/system/update-packages', methods=["POST"])
@authorized_personnel_only
def do_updates():
	utils.shell("check_call", ["/usr/bin/apt-get", "-qq", "update"])
	return utils.shell("check_output", ["/usr/bin/apt-get", "-y", "upgrade"], env={
		"DEBIAN_FRONTEND": "noninteractive"
	})

# APP

if __name__ == '__main__':
	if "DEBUG" in os.environ: app.debug = True

	if not app.debug:
		app.logger.addHandler(utils.create_syslog_handler())

	# For testing on the command line, you can use `curl` like so:
	#    curl --user $(</var/lib/mailinabox/api.key): http://localhost:10222/mail/users
	auth_service.write_key()

	# For testing in the browser, you can copy the API key that's output to the
	# debug console and enter that as the username
	app.logger.info('API key: ' + auth_service.key)

	app.run(port=10222)

