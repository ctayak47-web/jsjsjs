"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { createUserWithEmailAndPassword } from "firebase/auth";
import { auth, db } from "@/lib/firebase/config";
import { doc, setDoc } from "firebase/firestore";
import { Button } from "@/components/common/Button";
import { Icons } from "@/components/icons/IconSystem";
import toast from "react-hot-toast";

export default function RegisterPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();

    if (password !== confirmPassword) {
      toast.error("Passwords do not match");
      return;
    }

    if (password.length < 6) {
      toast.error("Password must be at least 6 characters");
      return;
    }

    setIsLoading(true);

    try {
      const { user } = await createUserWithEmailAndPassword(
        auth,
        email,
        password
      );

      // Create user document
      await setDoc(doc(db, "users", user.uid), {
        email: user.email,
        createdAt: Date.now(),
        updatedAt: Date.now(),
        lastSeen: Date.now(),
      });

      // Create profile document
      await setDoc(doc(db, "profiles", user.uid), {
        uid: user.uid,
        username: email.split("@")[0],
        displayName: "",
        bio: "",
        verified: false,
        privacySettings: {
          allowMessages: true,
          allowGiftTransfer: true,
          showOnlineStatus: true,
        },
      });

      // Create star balance
      await setDoc(doc(db, "starBalances", user.uid), {
        balance: 100, // Starter bonus
        lifetime: 100,
        updatedAt: Date.now(),
      });

      toast.success("Account created successfully!");
      router.push("/chats");
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Registration failed";
      toast.error(message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen px-6 gap-6">
      <div className="text-center mb-4">
        <h1 className="text-3xl font-bold">Create Account</h1>
        <p className="text-gray-500 dark:text-gray-400 mt-2">
          Join CrolGram today
        </p>
      </div>

      <form onSubmit={handleRegister} className="w-full max-w-sm space-y-4">
        <div>
          <label className="text-sm font-medium block mb-2">Email</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@example.com"
            required
            className="w-full px-4 py-3 rounded-lg border border-cg-border-light dark:border-cg-border-dark bg-cg-surface-light dark:bg-cg-surface-dark focus:outline-none focus:ring-2 focus:ring-cg-primary"
          />
        </div>

        <div>
          <label className="text-sm font-medium block mb-2">Password</label>
          <div className="relative">
            <input
              type={showPassword ? "text" : "password"}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="At least 6 characters"
              required
              className="w-full px-4 py-3 rounded-lg border border-cg-border-light dark:border-cg-border-dark bg-cg-surface-light dark:bg-cg-surface-dark focus:outline-none focus:ring-2 focus:ring-cg-primary"
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-3 top-3 text-gray-500"
            >
              {showPassword ? (
                <Icons.EyeOff size={20} />
              ) : (
                <Icons.Eye size={20} />
              )}
            </button>
          </div>
        </div>

        <div>
          <label className="text-sm font-medium block mb-2">
            Confirm Password
          </label>
          <input
            type={showPassword ? "text" : "password"}
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            placeholder="Confirm your password"
            required
            className="w-full px-4 py-3 rounded-lg border border-cg-border-light dark:border-cg-border-dark bg-cg-surface-light dark:bg-cg-surface-dark focus:outline-none focus:ring-2 focus:ring-cg-primary"
          />
        </div>

        <Button
          variant="primary"
          size="lg"
          className="w-full"
          isLoading={isLoading}
          type="submit"
        >
          Create Account
        </Button>
      </form>

      <div className="text-center text-sm text-gray-500">
        <p>
          Already have an account?{" "}
          <button
            onClick={() => router.push("/login")}
            className="text-cg-primary hover:underline"
          >
            Login
          </button>
        </p>
      </div>
    </div>
  );
}
