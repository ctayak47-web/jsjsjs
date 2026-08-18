"use client";

import { useAuthStore } from "@/store/authStore";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { LoadingSpinner } from "@/components/common/LoadingSpinner";
import { Card } from "@/components/common/Card";
import { Icons } from "@/components/icons/IconSystem";
import { Button } from "@/components/common/Button";
import { signOut } from "firebase/auth";
import { auth, db } from "@/lib/firebase/config";
import { doc, getDoc } from "firebase/firestore";
import { Profile } from "@/types";
import toast from "react-hot-toast";

export default function ProfilePage() {
  const router = useRouter();
  const { uid, isLoading, logout } = useAuthStore();
  const [profile, setProfile] = useState<Profile | null>(null);
  const [stars, setStars] = useState(0);
  const [profileLoading, setProfileLoading] = useState(true);

  useEffect(() => {
    if (!isLoading && !uid) {
      router.push("/login");
    }
  }, [uid, isLoading, router]);

  useEffect(() => {
    if (uid) {
      const loadProfile = async () => {
        try {
          const profileDoc = await getDoc(doc(db, "profiles", uid));
          if (profileDoc.exists()) {
            setProfile(profileDoc.data() as Profile);
          }

          const starsDoc = await getDoc(doc(db, "starBalances", uid));
          if (starsDoc.exists()) {
            setStars(starsDoc.data().balance);
          }
        } catch (error) {
          console.error("Failed to load profile:", error);
        } finally {
          setProfileLoading(false);
        }
      };

      loadProfile();
    }
  }, [uid]);

  const handleLogout = async () => {
    try {
      await signOut(auth);
      logout();
      toast.success("Logged out successfully");
      router.push("/login");
    } catch (error) {
      toast.error("Failed to logout");
    }
  };

  if (isLoading || profileLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner fullScreen />
      </div>
    );
  }

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-6">Profile</h1>

      {/* Profile Header */}
      <Card className="mb-6">
        <div className="flex items-start gap-4">
          <div className="w-16 h-16 rounded-full bg-gradient-to-br from-cg-primary to-cg-secondary flex-shrink-0" />
          <div className="flex-1">
            <div className="flex items-center gap-2">
              <h2 className="text-xl font-bold">{profile?.displayName || "User"}</h2>
              {profile?.verified && (
                <Icons.Verified size={20} className="text-cg-primary" />
              )}
            </div>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              @{profile?.username}
            </p>
            <p className="text-sm mt-2">{profile?.bio || "No bio yet"}</p>
          </div>
        </div>
      </Card>

      {/* Stats */}
      <div className="grid grid-cols-2 gap-3 mb-6">
        <Card>
          <div className="text-center">
            <p className="text-xs text-gray-500 dark:text-gray-400">CG Stars</p>
            <div className="flex items-center justify-center gap-1 mt-1">
              <Icons.Star size={20} className="text-yellow-500" />
              <p className="text-2xl font-bold">{stars}</p>
            </div>
          </div>
        </Card>
        <Card>
          <div className="text-center">
            <p className="text-xs text-gray-500 dark:text-gray-400">
              Gifts
            </p>
            <p className="text-2xl font-bold mt-1">0</p>
          </div>
        </Card>
      </div>

      {/* Actions */}
      <div className="space-y-3 mb-6">
        <Button variant="secondary" className="w-full justify-start">
          <Icons.User size={20} className="mr-2" />
          Edit Profile
        </Button>
        <Button variant="secondary" className="w-full justify-start">
          <Icons.Bell size={20} className="mr-2" />
          Notifications
        </Button>
        <Button variant="secondary" className="w-full justify-start">
          <Icons.Settings size={20} className="mr-2" />
          Settings
        </Button>
      </div>

      <Button
        variant="danger"
        size="lg"
        className="w-full"
        onClick={handleLogout}
      >
        Logout
      </Button>
    </div>
  );
}
