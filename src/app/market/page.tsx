"use client";

import { useAuthStore } from "@/store/authStore";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { LoadingSpinner } from "@/components/common/LoadingSpinner";
import { Icons } from "@/components/icons/IconSystem";

export default function MarketPage() {
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
        <h1 className="text-2xl font-bold">Marketplace</h1>
        <div className="flex gap-2">
          <button className="p-2 rounded-lg bg-cg-surface-light dark:bg-cg-surface-dark">
            <Icons.Search size={20} />
          </button>
        </div>
      </div>

      <div className="mt-12 flex flex-col items-center justify-center gap-4">
        <Icons.ShoppingCart size={48} className="text-gray-300 dark:text-gray-700" />
        <p className="text-gray-500 dark:text-gray-400 text-center">
          No listings available
        </p>
      </div>
    </div>
  );
}
