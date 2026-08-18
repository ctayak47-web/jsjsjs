# CrolGram Deployment Guide

## Firebase Setup

### 1. Create Firebase Project

- Go to [Firebase Console](https://console.firebase.google.com)
- Create new project "CrolGram"
- Enable Google Analytics (optional)

### 2. Enable Authentication

- Go to Authentication > Sign-in method
- Enable Email/Password provider
- Save

### 3. Setup Firestore Database

- Go to Firestore Database > Create Database
- Choose production mode
- Start location: US (or your region)
- Click Create

### 4. Deploy Security Rules

```bash
npm install -g firebase-tools
firebase init
# Select: Firestore, Hosting, Functions
# When asked about config, paste contents of firestore.rules
firebase deploy --only firestore:rules
```

### 5. Add Collections (via Firebase Console)

Create empty collections:
- `users`
- `profiles`
- `numbers`
- `chats`
- `gifts`
- `giftInventory`
- `starBalances`
- `marketListings`
- `trades`
- `notifications`

### 6. Create Web App

- Project Settings > Your apps
- Click "Add app" > Web
- Copy config to `.env.local`

### 7. Storage Setup (for images)

- Go to Storage > Get Started
- Start in production mode
- Set up rules for file uploads

Update storage rules:

```
rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {
    match /{allPaths=**} {
      allow read: if true;
      allow write: if request.auth != null;
    }
  }
}
```

## Vercel Deployment

### 1. Push to GitHub

```bash
git add .
git commit -m "Initial CrolGram commit"
git push origin main
```

### 2. Connect to Vercel

- Go to [Vercel Dashboard](https://vercel.com/dashboard)
- Click "New Project"
- Select your GitHub repository
- Configure project:
  - Framework: Next.js
  - Root Directory: ./
  - Install command: `npm install`
  - Build command: `npm run build`
  - Start command: `npm start`

### 3. Add Environment Variables

In Vercel Project Settings > Environment Variables:

```
NEXT_PUBLIC_FIREBASE_API_KEY
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN
NEXT_PUBLIC_FIREBASE_PROJECT_ID
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID
NEXT_PUBLIC_FIREBASE_APP_ID
```

### 4. Configure Firestore CORS

If getting CORS errors, update Firebase Storage rules in Firebase Console.

### 5. Deploy

Click "Deploy" button or push to main branch for auto-deploy.

## Firebase Cloud Functions (for advanced features)

### Create functions project

```bash
firebase init functions
cd functions
npm install
```

### Example: Process gift purchase

```typescript
// functions/src/index.ts
import * as functions from "firebase-functions";
import * as admin from "firebase-admin";

admin.initializeApp();
const db = admin.firestore();

export const purchaseGift = functions.https.onCall(async (data, context) => {
  if (!context.auth) throw new Error("Not authenticated");
  
  const uid = context.auth.uid;
  const { giftId, price } = data;
  
  // Use transaction for atomicity
  return db.runTransaction(async (transaction) => {
    const userRef = db.collection("starBalances").doc(uid);
    const userDoc = await transaction.get(userRef);
    
    if (!userDoc.exists) throw new Error("User not found");
    
    const balance = userDoc.data()!.balance;
    if (balance < price) throw new Error("Insufficient stars");
    
    // Deduct stars
    transaction.update(userRef, {
      balance: balance - price,
      updatedAt: admin.firestore.FieldValue.serverTimestamp(),
    });
    
    // Add to inventory
    transaction.set(db.collection("giftInventory").doc(uid).collection("gifts").doc(), {
      giftId,
      owner: uid,
      level: 0,
      acquiredAt: admin.firestore.FieldValue.serverTimestamp(),
      status: "owned",
    });
    
    return { success: true };
  });
});
```

### Deploy functions

```bash
firebase deploy --only functions
```

## Custom Domain

1. Go to Vercel Project > Settings > Domains
2. Add your custom domain
3. Update DNS records according to Vercel instructions

## Monitoring

### Firebase Console
- Analytics
- Performance
- Error reporting

### Vercel Analytics
- Page performance
- Core Web Vitals
- User analytics

## Backup Strategy

- Firebase Firestore automatic backups (Daily)
- Enable Cloud Backup (if using Blaze plan)
- Regular manual exports

## Scaling

- Start with Spark plan (free tier)
- Move to Blaze when needed for functions/storage
- Set up billing alerts
- Optimize Firestore queries with indexes

## SSL/TLS

Automatic via Vercel and Firebase domains.

## API Rate Limiting

Implement in Cloud Functions:

```typescript
import * as rateLimit from "express-rate-limit";

const limiter = rateLimit.default({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // limit each IP to 100 requests per windowMs
});
```

## Contact & Support

For Firebase issues: [Firebase Support](https://firebase.google.com/support)
For Vercel issues: [Vercel Support](https://vercel.com/support)
