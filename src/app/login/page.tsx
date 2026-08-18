"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { signInWithEmailAndPassword } from "firebase/auth";
import { auth } from "@/lib/firebase/config";
import { Button } from "@/components/common/Button";
import { Icons } from "@/components/icons/IconSystem";
import toast from "react-hot-toast";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      await signInWithEmailAndPassword(auth, email, password);
      toast.success("Logged in successfully!");
      router.push("/chats");
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Login failed";
      toast.error(message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen px-6 gap-6">
      <div className="text-center mb-4">
        <h1 className="text-3xl font-bold">Login</h1>
        <p className="text-gray-500 dark:text-gray-400 mt-2">
          Welcome back to CrolGram
        </p>
      </div>

      <form onSubmit={handleLogin} className="w-full max-w-sm space-y-4">
        <div>
          <label className="text-sm font-medium block mb-2">Email</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@example.com"
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
              placeholder="••••••••"
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

        <Button
          variant="primary"
          size="lg"
          className="w-full"
          isLoading={isLoading}
          type="submit"
        >
          Login
        </Button>
      </form>

      <div className="text-center text-sm text-gray-500">
        <p>
          Don't have an account?{" "}
          <button
            onClick={() => router.push("/register")}
            className="text-cg-primary hover:underline"
          >
            Sign up
          </button>
        </p>
      </div>
    </div>
  );
}
