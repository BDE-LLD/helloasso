# helloasso.py

A really simple script that lets you track who and how many people bought a ticket to an event on helloasso

There are only 3 commands

## save

`./helloasso.py save` will get the list of tickets and save it in `users.csv`

## check

`./helloasso.py check` will check if there are new sells.
I recommend to use it with a crontab such as :

```sh
*·*·*·*·*·/path/to/helloasso.py check
```

If you set a discord `WEBHOOK_URL` it will send the same print by webhook

## list

`./helloasso.py list` will print back the users

# .env

You must set a .env file in the same folder that contain :

```sh
WEBHOOK_URL=""
HELLOASSO_CLIENT_ID=""
HELLOASSO_CLIENT_SECRET=""
```

# congig.json

I let what I use as config for exemple
