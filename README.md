Mail-in-a-Box
=============

By [@JoshData](https://github.com/JoshData) and contributors.

Mail-in-a-Box helps individuals take back control of their email by defining a one-click, easy-to-deploy SMTP+everything else server: a mail server in a box.

**This is a work in progress. I work on this in my limited free time.**

Why build this? Mass electronic surveillance by governments revealed over the last year has spurred a new movement to [re-decentralize](http://redecentralize.org/) the web, that is, to empower netizens to be their own service providers again. SMTP, the protocol of email, is decentralized in principle but highly centralized in practice due to the high cost of implementing all of the modern protocols that surround it. As a result, most individuals trade their independence for access to a “free” email service.


The Box
-------

Mail-in-a-Box turns a fresh Ubuntu 14.04 LTS 64-bit machine into a working mail server, including SMTP ([postfix](http://www.postfix.org/)), IMAP ([dovecot](http://dovecot.org/)), Exchange ActiveSync ([z-push](https://github.com/fmbiete/Z-Push-contrib)), webmail ([Roundcube](http://roundcube.net/)), spam filtering ([spamassassin](https://spamassassin.apache.org/)), greylisting ([postgrey](http://postgrey.schweikert.ch/)), CardDAV/CalDAV ([ownCloud](http://owncloud.org/)), DNS, [SPF](https://en.wikipedia.org/wiki/Sender_Policy_Framework), DKIM ([OpenDKIM](http://www.opendkim.org/)), [DMARC](https://en.wikipedia.org/wiki/DMARC), [DNSSEC](https://en.wikipedia.org/wiki/DNSSEC), [DANE TLSA](https://en.wikipedia.org/wiki/DNS-based_Authentication_of_Named_Entities), and basic system services like a firewall, intrusion protection, and setting the system clock.

This setup is what has been powering my own personal email since September 2013.

Please see [mailinabox.email](https://mailinabox.email) for more information and how to set up a Mail-in-a-Box.

In short, it's like this:

	# do this on a fresh install of Ubuntu 14.04 only!
	sudo apt-get install -y git
	git clone https://github.com/mail-in-a-box/mailinabox
	cd mailinabox
	sudo setup/start.sh

Congratulations! You should now have a working setup. You'll be given the address of the administrative interface for further instructions.

**Status**: This is a work in progress. It works for what it is, but it is missing such things as quotas, backup/restore, etc.

The Goals
---------

I am trying to:

* Make deploying a good mail server easy.
* Promote [decentralization](http://redecentralize.org/), innovation, and privacy on the web.
* Have automated, auditable, and [idempotent](http://sharknet.us/2014/02/01/automated-configuration-management-challenges-with-idempotency/) configuration.
* **Not** to be a mail server that the NSA cannot hack.
* **Not** to be customizable by power users.

For more background, see [The Rationale](https://github.com/mail-in-a-box/mailinabox/wiki).

The Acknowledgements
--------------------

This project was inspired in part by the ["NSA-proof your email in 2 hours"](http://sealedabstract.com/code/nsa-proof-your-e-mail-in-2-hours/) blog post by Drew Crawford, [Sovereign](https://github.com/al3x/sovereign) by Alex Payne, and conversations with <a href="http://twitter.com/shevski" target="_blank">@shevski</a>, <a href="https://github.com/konklone" target="_blank">@konklone</a>, and <a href="https://github.com/gregelin" target="_blank">@GregElin</a>.

Mail-in-a-Box is similar to [iRedMail](http://www.iredmail.org/).

The History
-----------

* In 2007 I wrote a relatively popular Mozilla Thunderbird extension that added client-side SPF and DKIM checks to mail to warn users about possible phishing: [add-on page](https://addons.mozilla.org/en-us/thunderbird/addon/sender-verification-anti-phish/), [source](https://github.com/JoshData/thunderbird-spf).
* Mail-in-a-Box was a semifinalist in the 2014 [Knight News Challenge](https://www.newschallenge.org/challenge/2014/submissions/mail-in-a-box), but it was not selected as a winner.
