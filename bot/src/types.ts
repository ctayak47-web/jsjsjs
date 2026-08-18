export interface TelegramUser {
  telegramId: number;
  username?: string;
  firstName: string;
  lastName?: string;
  linkedCrolGramUid?: string;
  createdAt: number;
}

export interface UserSession {
  telegramId: number;
  state: "main" | "get_free_number" | "buy_number" | "my_numbers" | "buy_stars";
  data: Record<string, any>;
  createdAt: number;
  updatedAt: number;
}

export interface CrolGramNumber {
  numberId: string;
  formattedNumber: string;
  country: string;
  type: "free" | "premium" | "special";
  owner?: string;
  isActive: boolean;
  purchasedAt?: number;
  price?: number;
}

export interface AvailableNumber {
  numberId: string;
  formattedNumber: string;
  country: string;
  type: "free" | "premium";
  price?: number;
}
