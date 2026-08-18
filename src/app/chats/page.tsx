"use client";

import { useAuthStore } from "@/store/authStore";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { LoadingSpinner } from "@/components/common/LoadingSpinner";
import { Card } from "@/components/common/Card";
import { Icons } from "@/components/icons/IconSystem";
import { Button } from "@/components/common/Button";

export default function ChatsPage() {
  const router = useRouter();
  const { uid, isLoading } = useAuthStore();

  useEffect(() => {
    if (!isLoading && !uid) {
      router.push("/login");
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
    <div className="p-4">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Chats</h1>
        <Button variant="ghost" size="sm">
          <Icons.Plus size={24} />
        </Button>
      </div>

      <div className="space-y-2">
        <Card interactive className="p-0 overflow-hidden">
          <div className="p-4 flex items-center gap-3">
            <div className="w-12 h-12 rounded-full bg-gradient-to-br from-cg-primary to-cg-secondary" />
            <div className="flex-1 min-w-0">
              <p className="font-semibold truncate">Welcome to CrolGram</p>
              <p className="text-sm text-gray-500 dark:text-gray-400 truncate">
                Start messaging and collecting
              </p>
            </div>
          </div>
        </Card>
      </div>

      <div className="mt-12 flex flex-col items-center justify-center gap-4">
        <Icons.Message size={48} className="text-gray-300 dark:text-gray-700" />
        <p className="text-gray-500 dark:text-gray-400 text-center">
          No chats yet. Start a conversation!
        </p>
        <Button variant="primary">Start Chat</Button>
      </div>
    </div>
  );
}
