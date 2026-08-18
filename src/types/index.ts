export interface User {
  uid: string;
  email: string;
  createdAt: number;
  updatedAt: number;
  lastSeen: number;
}

export interface Profile {
  uid: string;
  username: string;
  displayName: string;
  bio: string;
  avatar?: string;
  banner?: string;
  verified: boolean;
  privacySettings: {
    allowMessages: boolean;
    allowGiftTransfer: boolean;
    showOnlineStatus: boolean;
  };
}

export interface CrolGramNumber {
  numberId: string;
  formattedNumber: string;
  country: string;
  type: 'free' | 'premium' | 'special';
  owner?: string;
  isActive: boolean;
  purchasedAt?: number;
  expiresAt?: number;
}

export interface Chat {
  chatId: string;
  type: 'direct' | 'group' | 'channel';
  members: string[];
  lastMessage?: string;
  lastMessageAt?: number;
  createdAt: number;
  name?: string;
  avatar?: string;
  unreadCount: number;
}

export interface Message {
  messageId: string;
  chatId: string;
  author: string;
  text: string;
  media?: string[];
  reactions?: Record<string, string[]>;
  editedAt?: number;
  deletedAt?: number;
  replyTo?: string;
  status: 'sending' | 'sent' | 'read';
  timestamp: number;
}

export interface Gift {
  giftId: string;
  name: string;
  description: string;
  imageUrl: string;
  rarity: 'common' | 'rare' | 'epic' | 'legendary';
  basePrice: number;
  totalEditions: number;
  createdAt: number;
}

export interface GiftInventory {
  inventoryId: string;
  giftId: string;
  owner: string;
  level: number;
  acquiredAt: number;
  status: 'owned' | 'listed' | 'locked_trade';
  rarity: string;
  upgradedAt?: number;
}

export interface MarketListing {
  listingId: string;
  giftInventoryId: string;
  seller: string;
  price: number;
  rarity: string;
  level: number;
  status: 'active' | 'sold' | 'cancelled';
  createdAt: number;
  soldAt?: number;
  buyer?: string;
}

export interface Trade {
  tradeId: string;
  initiator: string;
  responder: string;
  offers: {
    initiator: {
      giftIds: string[];
      stars: number;
    };
    responder: {
      giftIds: string[];
      stars: number;
    };
  };
  status: 'pending' | 'accepted' | 'rejected' | 'completed';
  createdAt: number;
  expiresAt: number;
  completedAt?: number;
}

export interface StarBalance {
  uid: string;
  balance: number;
  lifetime: number;
  updatedAt: number;
}

export interface StarTransaction {
  txId: string;
  type: 'purchase' | 'gift_buy' | 'gift_upgrade' | 'market_buy' | 'gift_transfer' | 'starter_bonus' | 'trade';
  amount: number;
  reference?: string;
  status: 'pending' | 'completed' | 'failed';
  timestamp: number;
  metadata?: Record<string, any>;
}

export interface Notification {
  notifId: string;
  type: 'message' | 'gift_received' | 'trade_request' | 'market_listing';
  read: boolean;
  data: Record<string, any>;
  createdAt: number;
  action?: string;
}

export interface Country {
  countryCode: string;
  name: string;
  flag: string;
  availableNumbers: number;
  premiumCategories: string[];
}
