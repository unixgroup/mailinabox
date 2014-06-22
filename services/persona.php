<?php
	/* Mozilla Persona
	 * ***************
	 * 1) Outputs the /.well-known/browserid JSON file.
	 * 2) Handles login/provisioning URLs.
	 */

	// Parse our configuration file.
	$ENV = array();
	foreach (file("/etc/mailinabox.conf") as $line) {
		$line = explode("=", rtrim($line), 2);
		$ENV[ $line[0] ] = $line[1];
	}
	if ($ENV['STORAGE_ROOT'] == NULL) exit("no STORAGE_ROOT");
	if ($ENV['PUBLIC_HOSTNAME'] == NULL) exit("no PUBLIC_HOSTNAME");

	if ($_SERVER['DOCUMENT_URI'] == '/.well-known/browserid') {
		// Output the browserid JSON document.

		// If the browserid is being requested on a domain other than
		// PUBLIC_HOSTNAME, delegate authority to PUBLIC_HOSTNAME so
		// that user logins tend to be handled off of the same domain.
		// This is sort of nice for keeping the users' cookies in one
		// place.
		if ($_SERVER['SERVER_NAME'] != $ENV['PUBLIC_HOSTNAME']) {
			header("Content-type: application/json");
			echo(json_encode(array(
				"authority" => $ENV['PUBLIC_HOSTNAME']
			), JSON_PRETTY_PRINT));
			exit;
		}

		// Get our public key's modulus. Ugh needs padding?
		$public_key = rtrim(file_get_contents($ENV['STORAGE_ROOT'] . "/ssl/public_key_modulus.txt"));
		while (strlen($public_key) < 514)
			$public_key = "00" . $public_key;

		// Output.
		header("Content-type: application/json");
		echo(json_encode(array(
			"public-key" => array(
				"algorithm" => "RS",
				"n" => $public_key,
				"e" => "65537",
			),
			"authentication" => "/persona-login/sign-in",
	    	"provisioning" => "/persona-login/provision",
		), JSON_PRETTY_PRINT));
	}

	if ($_SERVER['DOCUMENT_URI'] == '/persona-login/sign-in') {
		// Create a login page for the user.

		?>
<!DOCTYPE html>
<html class="no-js">
    <head>
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
        <meta name="viewport" content="width=device-width">
        <title>Mozilla Persona Login</title>
        <link rel="stylesheet" href="//maxcdn.bootstrapcdn.com/bootstrap/3.1.1/css/bootstrap.min.css" />
    </head>
    <body>
    	<div class="container">
	    	<div class="row">
	    		<div class="col-sm-offset-2 col-sm-8 col-md-offset-3 col-md-6 col-lg-offset-3 col-lg-6">
	    			<center>
	    				<h1 style="margin: 1em">Mozilla Persona Login</h1>
	    			</center>

					<form class="form-horizontal" role="form" method="post">
					  <div class="form-group">
					    <label for="inputEmail3" class="col-sm-2 control-label">Email</label>
					    <div class="col-sm-10">
					      <input name="email" type="email" class="form-control" id="inputEmail" placeholder="Email">
					    </div>
					  </div>
					  <div class="form-group">
					    <label for="inputPassword3" class="col-sm-2 control-label">Password</label>
					    <div class="col-sm-10">
					      <input name="password" type="password" class="form-control" placeholder="Password">
					    </div>
					  </div>
					  <div class="form-group">
					    <div class="col-sm-offset-2 col-sm-10">
					      <div class="checkbox">
					        <label>
					          <input type="checkbox"> Remember me
					        </label>
					      </div>
					    </div>
					  </div>
					  <div class="form-group">
					    <div class="col-sm-offset-2 col-sm-10">
					      <button type="submit" class="btn btn-default">Sign in</button>
					    </div>
					  </div>
					</form>
	    		</div>
	    	</div>
    	</div>

    	<script src="//code.jquery.com/jquery-2.1.1.min.js"> </script>
        <script src="//maxcdn.bootstrapcdn.com/bootstrap/3.1.1/js/bootstrap.min.js"></script>
		<script src="https://login.persona.org/authentication_api.js"></script>
		<script>
			navigator.id.beginAuthentication(function(email) {
			  $('#inputEmail').val(email);
			});
		</script>
    </body>
</html>
<?php
	}

	if ($_SERVER['DOCUMENT_URI'] == '/persona-login/provision') {
		// Create the provisioning document that is used behind-the-scenes
		// by the browser.

		?>
<html>
	<head>
		<title>[Not For You] Mozilla Persona Provisioning Page</title>
		<script src="https://login.persona.org/provisioning_api.js"> </script>
		<script>
			navigator.id.beginProvisioning(function(email, certDuration) {
				 navigator.id.raiseProvisioningFailure("User is not logged in here yet.")
			});
		</script>
	</head>
	<body>
		This page is not meant to be visited directly.
	</body>
</html>
<?php
	}
?>

