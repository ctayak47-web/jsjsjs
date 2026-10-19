# Required subscription gate — option B

CrustyChess checks membership at every cold launch and before starting analysis.

## Trust model
- The APK never decides membership from a local flag.
- A Telegram bot must be an administrator of `@CrustySearch`.
- The backend calls Telegram Bot API `getChatMember` using the bot token stored only on the server.
- The app obtains a verified Telegram user identity through a secure login flow; never trust a client-supplied numeric user ID by itself.
- If membership is absent, block analysis and offer a link to `https://t.me/CrustySearch`.
- If Telegram/backend is unavailable, fail closed for starting analysis but show a retry option. Do not log the bot token or authentication secrets.
- Recheck on each cold launch and immediately before starting a new analysis session. Optionally recheck periodically during a long session.
- After the user returns from Telegram, call the backend again.

A channel link or an "I subscribed" button is not verification. Do not put the Telegram bot token in the Android app.
