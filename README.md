# Motivate

Motivate is a small webapp that promises to make you get done what you need to do by hurting you in your wallet if you don't.

Need something to help stop procrastinating? We've got your back. Motivate is designed to be simple but brutal on procrastination. You make tasks and send reports. 

Sounds too easy right? There's a twist: if you fail to send a report or send a funky report you lose money. That's it. We've found that giving people a monetary punishment is the best way to stop procrastination. 

You can stop or pause a task at anytime.

## Installation
Download and run 
	pip install -r requirements.txt

### Motivate needs a couple of environmental variables to start up
 * Need a database URL. Motivate uses sqlalchemy so any DB will do.
 
		export db="postgresql://yourpostgresURL"
 * We need a port variable and the host IP address
 
 		export port=80
	 	export host=YOURIP

 * Motivate uses Stripe to charge payments so we need your Stripe API Publishable Key and Secret Key. See the [Stripe API Guide](https://stripe.com/docs/checkout/guides/flask)
 
 		export PUBLISHABLE_KEY=yourStripePublishableKey
 		export SECRET_KEY=yourStripeSecretKey
 		
 * Motivate needs to send emails about reports and when reminders are send
 
 		export LOG_EMAIL=example@example.mail

### Motivate uses a Cron file for periodic tasks

* Install the Cron file by running in the top level Motivate folder:
		
		sudo ./setup_cron.sh
 		
## Running Motivate
* Motivate can be run using Gunicorn or Fab.

### To run Gunicorn
* Inside the top level Motivate folder

		gunicorn -w 4 -b YOURIP:YOURPORT runserver:app
		
### To run Fab
* Inside the top level Motivate folder
		
		fab runserver
		
		
		
## Administering Motivate
* Create a user with the username admin. 
* ##THE FIRST USER WITH THIS USERNAME WILL HAVE ADMIN PRIVILEGES

* When users create a task, they have to set reports every X days. When they send in a report, it gets added to the reports list that can be accessed at /approve . There you can approve or deny reports

* The cronjob runs at noon and 1 am. At noon, the cronjob checks for any denyed reports or users who did not make a report and charges them via Stripe. At 1 am, it sends all users who have a report the next day a reminder to do so via email.

That's about it. If you have any questions/run into any bugs, shoot me a message. I may have missed something so please tell me if I do.



