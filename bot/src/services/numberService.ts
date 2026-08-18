import { db } from "../firebase";
import { CrolGramNumber, AvailableNumber } from "../types";

export class NumberService {
  static async getFreeNumbers(country: string): Promise<AvailableNumber[]> {
    try {
      const snapshot = await db
        .collection("numbers")
        .where("country", "==", country)
        .where("type", "==", "free")
        .where("isActive", "==", true)
        .where("owner", "==", null)
        .limit(10)
        .get();

      return snapshot.docs.map((doc) => ({
        numberId: doc.id,
        formattedNumber: doc.data().formattedNumber,
        country: doc.data().country,
        type: doc.data().type,
      }));
    } catch (error) {
      console.error("Error fetching free numbers:", error);
      return [];
    }
  }

  static async getPremiumNumbers(country: string): Promise<AvailableNumber[]> {
    try {
      const snapshot = await db
        .collection("numbers")
        .where("country", "==", country)
        .where("type", "==", "premium")
        .where("isActive", "==", true)
        .where("owner", "==", null)
        .limit(20)
        .get();

      return snapshot.docs.map((doc) => ({
        numberId: doc.id,
        formattedNumber: doc.data().formattedNumber,
        country: doc.data().country,
        type: doc.data().type,
        price: doc.data().price || 0,
      }));
    } catch (error) {
      console.error("Error fetching premium numbers:", error);
      return [];
    }
  }

  static async assignFreeNumber(
    numberId: string,
    crolGramUid: string
  ): Promise<boolean> {
    try {
      await db.collection("numbers").doc(numberId).update({
        owner: crolGramUid,
        isActive: true,
        purchasedAt: Date.now(),
      });
      return true;
    } catch (error) {
      console.error("Error assigning number:", error);
      return false;
    }
  }

  static async getCountries(): Promise<
    { code: string; name: string; flag: string }[]
  > {
    try {
      const snapshot = await db.collection("countries").get();
      return snapshot.docs.map((doc) => ({
        code: doc.id,
        name: doc.data().name,
        flag: doc.data().flag,
      }));
    } catch (error) {
      console.error("Error fetching countries:", error);
      return [];
    }
  }

  static async getUserNumbers(crolGramUid: string): Promise<CrolGramNumber[]> {
    try {
      const snapshot = await db
        .collection("numbers")
        .where("owner", "==", crolGramUid)
        .get();

      return snapshot.docs.map((doc) => ({
        numberId: doc.id,
        formattedNumber: doc.data().formattedNumber,
        country: doc.data().country,
        type: doc.data().type,
        owner: doc.data().owner,
        isActive: doc.data().isActive,
        purchasedAt: doc.data().purchasedAt,
      }));
    } catch (error) {
      console.error("Error fetching user numbers:", error);
      return [];
    }
  }
}
