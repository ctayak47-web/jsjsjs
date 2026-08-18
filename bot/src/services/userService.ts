import { db } from "../firebase";
import { TelegramUser } from "../types";

export class UserService {
  static async getOrCreateTelegramUser(
    telegramId: number,
    firstName: string,
    username?: string,
    lastName?: string
  ): Promise<TelegramUser> {
    try {
      const doc = await db.collection("telegramUsers").doc(String(telegramId)).get();

      if (doc.exists) {
        return doc.data() as TelegramUser;
      }

      const newUser: TelegramUser = {
        telegramId,
        username,
        firstName,
        lastName,
        createdAt: Date.now(),
      };

      await db
        .collection("telegramUsers")
        .doc(String(telegramId))
        .set(newUser);

      return newUser;
    } catch (error) {
      console.error("Error in getOrCreateTelegramUser:", error);
      throw error;
    }
  }

  static async linkToCrolGram(
    telegramId: number,
    crolGramUid: string
  ): Promise<boolean> {
    try {
      await db
        .collection("telegramUsers")
        .doc(String(telegramId))
        .update({
          linkedCrolGramUid: crolGramUid,
        });
      return true;
    } catch (error) {
      console.error("Error linking to CrolGram:", error);
      return false;
    }
  }

  static async getTelegramUserByCrolGramUid(
    crolGramUid: string
  ): Promise<TelegramUser | null> {
    try {
      const snapshot = await db
        .collection("telegramUsers")
        .where("linkedCrolGramUid", "==", crolGramUid)
        .limit(1)
        .get();

      if (snapshot.empty) {
        return null;
      }

      return snapshot.docs[0].data() as TelegramUser;
    } catch (error) {
      console.error("Error getting Telegram user:", error);
      return null;
    }
  }

  static async saveUserSession(
    telegramId: number,
    state: string,
    data: Record<string, any>
  ): Promise<void> {
    try {
      await db
        .collection("telegramSessions")
        .doc(String(telegramId))
        .set({
          telegramId,
          state,
          data,
          createdAt: Date.now(),
          updatedAt: Date.now(),
        });
    } catch (error) {
      console.error("Error saving user session:", error);
    }
  }

  static async getUserSession(telegramId: number): Promise<any> {
    try {
      const doc = await db
        .collection("telegramSessions")
        .doc(String(telegramId))
        .get();

      return doc.exists ? doc.data() : null;
    } catch (error) {
      console.error("Error getting user session:", error);
      return null;
    }
  }
}
