"use client";

import { useRouter } from "next/navigation";
import { useAuthStore } from "@/store/authStore";
import { useEffect } from "react";
import { LoadingSpinner } from "@/components/common/LoadingSpinner";
import { Button } from "@/components/common/Button";
import { Icons } from "@/components/icons/IconSystem";

export default function Welcome() {
  const router = useRouter();
  const { uid, isLoading } = useAuthStore();

  useEffect(() => {
    if (!isLoading && uid) {
      router.push("/chats");
    }
  }, [uid, isLoading, router]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner fullScreen />
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-screen px-6 gap-8">
      <div className="text-center">
        <div className="text-6xl mb-4 flex justify-center">
          <Icons.Star size={64} className="text-cg-primary" />
        </div>
        <h1 className="text-4xl font-bold mb-2">CrolGram</h1>
        <p className="text-gray-500 dark:text-gray-400 text-lg">
          Premium messaging & collectibles
        </p>
      </div>

      <div className="w-full max-w-sm space-y-3">
        <Button
          variant="primary"
          size="lg"
          className="w-full"
          onClick={() => router.push("/login")}
        >
          Login
        </Button>
        <Button
          variant="secondary"
          size="lg"
          className="w-full"
          onClick={() => router.push("/register")}
        >
          Create Account
        </Button>
      </div>

      <div className="text-xs text-gray-400 text-center mt-8">
        <p>Premium messaging platform</p>
        <p>Collectible gifts & marketplace</p>
      </div>
    </div>
  );
}
