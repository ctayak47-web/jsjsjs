# CrolGram Telegram Bot

Entry point for CrolGram platform with number distribution and account linking.

## Features

- 📱 Get free CrolGram numbers
- 💎 Browse premium numbers
- 📋 View user numbers
- ⭐ Claim free CG Stars (coming)
- 💳 Buy CG Stars
- 🔐 Apply for verification
- 🔗 Link CrolGram account

## Setup

### 1. Get Bot Token

- Talk to [@BotFather](https://t.me/botfather) on Telegram
- Create new bot: `/newbot`
- Copy token

### 2. Environment

Create `.env`:

```bash
cp .env.example .env
# Add TELEGRAM_BOT_TOKEN and Firebase credentials
```

### 3. Install & Run

```bash
npm install
npm run dev
```

## Bot Menu

```
🎉 Welcome to CrolGram!

📱 Get Free Number     - Receive free CrolGram number
💎 Buy Beautiful Number - Purchase premium numbers
📋 My Numbers         - View your numbers
⭐ Get Free CG Stars   - Claim daily bonus
💳 Buy CG Stars       - Purchase stars
🔐 Get Verification   - Apply for verification badge
🌐 Open CrolGram Web  - Go to web app
```

## Commands

- `/start` - Main menu
- `/help` - Help

## Architecture

```
bot/src/
├── index.ts              # Main bot file
├── firebase.ts           # Firebase admin setup
├── types.ts              # TypeScript interfaces
├── handlers/
│   └── commands.ts       # Command handlers
└── services/
    ├── numberService.ts  # Number management
    └── userService.ts    # User management
```

## Data Flow

### Free Number Assignment

```
User clicks "Get Free Number"
    ↓
Select country
    ↓
Choose number
    ↓
Cloud Function: assignNumber()
    ├─ Check number availability
    ├─ Link to CrolGram account
    └─ Return success
    ↓
User gets confirmation
```

### Account Linking

```
CrolGram Web: Generate link code
    ↓
User sends code to bot
    ↓
Bot: Verify code via API
    ↓
Bot: Link telegramId → CrolGramUid
    ↓
User can now:
- Manage numbers
- Claim free stars
- View purchases
```

## Cloud Functions Needed

### 1. assignNumber()

```typescript
export const assignNumber = functions.https.onCall(async (data, context) => {
  const { numberId, countryCode } = data;
  const crolGramUid = context.auth?.uid;

  if (!crolGramUid) throw new Error("Not authenticated");

  return db.runTransaction(async (transaction) => {
    const numberRef = db.collection("numbers").doc(numberId);
    const numberDoc = await transaction.get(numberRef);

    if (!numberDoc.exists || numberDoc.data()!.owner) {
      throw new Error("Number not available");
    }

    transaction.update(numberRef, {
      owner: crolGramUid,
      isActive: true,
      purchasedAt: admin.firestore.FieldValue.serverTimestamp(),
    });

    return { success: true, number: numberDoc.data().formattedNumber };
  });
});
```

### 2. linkTelegramAccount()

```typescript
export const linkTelegramAccount = functions.https.onCall(async (data, context) => {
  const { telegramId, linkCode } = data;
  const crolGramUid = context.auth?.uid;

  if (!crolGramUid) throw new Error("Not authenticated");

  // Verify link code (generated on frontend, short-lived)
  const linkRef = db.collection("pendingLinks").doc(linkCode);
  const linkDoc = await linkRef.get();

  if (!linkDoc.exists || linkDoc.data()!.expiresAt < Date.now()) {
    throw new Error("Invalid or expired link code");
  }

  // Link accounts
  await db
    .collection("telegramUsers")
    .doc(String(telegramId))
    .update({ linkedCrolGramUid: crolGramUid });

  // Delete used link
  await linkRef.delete();

  return { success: true };
});
```

## Deployment

### Option 1: Cloud Run

```bash
gcloud run deploy crolg-bot \
  --source . \
  --set-env-vars TELEGRAM_BOT_TOKEN=xxx \
  --platform managed \
  --region us-central1
```

### Option 2: VPS

```bash
npm install
npm run build
npm start
```

## Logging

Logs go to Firebase Cloud Logging. Check via:

```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=crolg-bot" --limit 50
```

## Rate Limiting

Implement via:

1. **Telegraf middleware** - per user
2. **Firestore** - track API calls
3. **Cloud Functions** - rate limit via auth

Example:

```typescript
// Add to firestore.ts
async function checkRateLimit(telegramId: number, action: string) {
  const key = `ratelimit_${telegramId}_${action}`;
  const doc = await db.collection("rateLimits").doc(key).get();

  if (doc.exists) {
    const count = doc.data().count;
    if (count > 10) throw new Error("Rate limit exceeded");
  }
}
```

## Monitoring

- Firebase Console > Logging
- Telegram Bot API errors
- Check `/getupdates` endpoint

## Testing

```bash
# Test locally with webhook (requires HTTPS tunnel)
npm run dev
# Use ngrok: ngrok http 3000
```

## Next Steps

- [ ] Link code generation on CrolGram Web
- [ ] Cloud Functions for number assignment
- [ ] Payment integration (Stripe/PayPal)
- [ ] Daily free stars claim
- [ ] Verification requests
- [ ] Admin bot commands
