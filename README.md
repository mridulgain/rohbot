## ways to create bot server:
1. Polling: Our makes an out-bound connection from replit instance to Telegram, then relied on Telegram sending messages down that connection for processing.
2. With webhooks: things are reversed. We essentially tell Telegram, “when my bot receives a message, connect to replit and pass on the message”. And the “connect to repelit” bit is done by creating a web application to run inside your repelit account that will serve a really simple API.

## Overcoming free tier limitation:
Add a monitor in [UptimeRobot](https://uptimerobot.com/)
