import { useEffect } from "react";
import { onAuthStateChanged } from "firebase/auth";
import { auth, db } from "@/lib/firebase/config";
import { doc, getDoc } from "firebase/firestore";
import { useAuthStore } from "@/store/authStore";
import { User } from "@/types";

export function useAuth() {
  const { user, uid, isLoading, error, setUser, setLoading, setError } =
    useAuthStore();

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (firebaseUser) => {
      try {
        if (firebaseUser) {
          const userDoc = await getDoc(doc(db, "users", firebaseUser.uid));
          const userData: User = {
            uid: firebaseUser.uid,
            email: firebaseUser.email || "",
            createdAt: userDoc.data()?.createdAt || Date.now(),
            updatedAt: userDoc.data()?.updatedAt || Date.now(),
            lastSeen: Date.now(),
          };
          setUser(userData);
        } else {
          setUser(null);
        }
      } catch (err) {
        setError((err as Error).message);
        setUser(null);
      } finally {
        setLoading(false);
      }
    });

    return () => unsubscribe();
  }, [setUser, setLoading, setError]);

  return { user, uid, isLoading, error };
}
