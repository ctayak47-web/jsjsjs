import React, { ReactNode } from "react";
import { usePathname } from "next/navigation";
import Link from "next/link";
import { Icons } from "@/components/icons/IconSystem";
import clsx from "clsx";

interface NavItem {
  href: string;
  label: string;
  icon: React.ReactNode;
}

const NAV_ITEMS: NavItem[] = [
  {
    href: "/chats",
    label: "Chats",
    icon: <Icons.Message size={24} />,
  },
  {
    href: "/contacts",
    label: "Contacts",
    icon: <Icons.User size={24} />,
  },
  {
    href: "/gifts",
    label: "Gifts",
    icon: <Icons.Gift size={24} />,
  },
  {
    href: "/market",
    label: "Market",
    icon: <Icons.ShoppingCart size={24} />,
  },
  {
    href: "/profile",
    label: "Profile",
    icon: <Icons.User size={24} />,
  },
];

export function MobileShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();

  const isAuthPage =
    pathname === "/login" ||
    pathname === "/register" ||
    pathname === "/welcome" ||
    pathname === "/";

  return (
    <div
      className={clsx(
        "flex flex-col h-screen bg-cg-bg-light dark:bg-cg-bg-dark amoled:bg-cg-bg-amoled",
        "text-gray-900 dark:text-white"
      )}
    >
      {/* Safe area top */}
      <div className="h-safe-t" />

      {/* Main content */}
      <main
        className={clsx(
          "flex-1 overflow-y-auto",
          !isAuthPage && "pb-20"
        )}
      >
        {children}
      </main>

      {/* Bottom Navigation */}
      {!isAuthPage && (
        <>
          <div className="h-20" />
          <nav
            className={clsx(
              "fixed bottom-0 left-0 right-0 w-full z-50",
              "border-t border-cg-border-light dark:border-cg-border-dark",
              "bg-cg-bg-light dark:bg-cg-bg-dark amoled:bg-cg-bg-amoled",
              "backdrop-blur-xl bg-opacity-90 dark:bg-opacity-90",
              "flex justify-around items-center",
              "h-20 pb-safe-b"
            )}
          >
            {NAV_ITEMS.map((item) => {
              const isActive = pathname.startsWith(item.href);
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={clsx(
                    "flex flex-col items-center justify-center flex-1 h-20",
                    "transition-colors duration-200",
                    isActive
                      ? "text-cg-primary"
                      : "text-gray-500 dark:text-gray-400"
                  )}
                  title={item.label}
                >
                  {item.icon}
                  <span className="text-xs mt-1">{item.label}</span>
                </Link>
              );
            })}
          </nav>
        </>
      )}
    </div>
  );
}
