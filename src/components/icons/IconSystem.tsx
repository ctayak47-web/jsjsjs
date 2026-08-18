import React from "react";

interface IconProps {
  size?: number;
  className?: string;
}

export const Icons = {
  Star: ({ size = 24, className = "" }: IconProps) => (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="currentColor"
      className={className}
    >
      <path d="M12 2L15.09 8.26H22L17.55 12.51L19.64 18.77L12 14.51L4.36 18.77L6.45 12.51L2 8.26H8.91L12 2Z" />
    </svg>
  ),

  Message: ({ size = 24, className = "" }: IconProps) => (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="currentColor"
      className={className}
    >
      <path d="M20 2H4C2.9 2 2 2.9 2 4V22L6 18H20C21.1 18 22 17.1 22 16V4C22 2.9 21.1 2 20 2Z" />
    </svg>
  ),

  User: ({ size = 24, className = "" }: IconProps) => (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="currentColor"
      className={className}
    >
      <path d="M12 12C14.21 12 16 10.21 16 8C16 5.79 14.21 4 12 4C9.79 4 8 5.79 8 8C8 10.21 9.79 12 12 12ZM12 14C9.33 14 4 15.34 4 18V20H20V18C20 15.34 14.67 14 12 14Z" />
    </svg>
  ),

  Gift: ({ size = 24, className = "" }: IconProps) => (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="currentColor"
      className={className}
    >
      <path d="M20 8H4V4H20M19 12H5V20H19M12 1C12.55 1 13 1.45 13 2V3H19C20.11 3 21 3.89 21 5V8C22.11 8 23 8.89 23 10V20C23 21.11 22.11 22 21 22H3C1.89 22 1 21.11 1 20V10C1 8.89 1.89 8 3 8V5C3 3.89 3.89 3 5 3H11V2C11 1.45 11.45 1 12 1Z" />
    </svg>
  ),

  ShoppingCart: ({ size = 24, className = "" }: IconProps) => (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="currentColor"
      className={className}
    >
      <path d="M7 18C5.9 18 5 18.9 5 20C5 21.1 5.9 22 7 22C8.1 22 9 21.1 9 20C9 18.9 8.1 18 7 18ZM1 2V4H3L6.6 11.59L5.24 14.04C5.09 14.32 5 14.65 5 15C5 16.1 5.9 17 7 17H19V15H7.42C7.14 15 6.92 14.78 6.92 14.5C6.92 14.32 7 14.15 7.1 14.02L8.48 11.5H17.32C18.16 11.5 18.91 11.08 19.3 10.42L22.87 4.01C23.05 3.71 23.2 3.3 23.2 2.9C23.2 2.37 22.75 1.9 22.2 1.9H5.21L4.27 0H0V2ZM17 18C15.9 18 15 18.9 15 20C15 21.1 15.9 22 17 22C18.1 22 19 21.1 19 20C19 18.9 18.1 18 17 18Z" />
    </svg>
  ),

  Settings: ({ size = 24, className = "" }: IconProps) => (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="currentColor"
      className={className}
    >
      <path d="M19.14 12.94C19.18 12.64 19.2 12.33 19.2 12C19.2 11.67 19.18 11.36 19.14 11.06L21.16 9.48C21.34 9.34 21.39 9.07 21.28 8.87L19.36 5.55C19.25 5.35 19.03 5.28 18.84 5.38L16.53 6.5C16.04 6.05 15.48 5.65 14.87 5.35L14.5 2.81C14.46 2.57 14.25 2.4 14 2.4H10C9.75 2.4 9.54 2.57 9.5 2.81L9.13 5.35C8.52 5.65 7.96 6.05 7.47 6.5L5.16 5.38C4.97 5.28 4.75 5.35 4.64 5.55L2.72 8.87C2.61 9.07 2.66 9.34 2.84 9.48L4.86 11.06C4.82 11.36 4.8 11.67 4.8 12C4.8 12.33 4.82 12.64 4.86 12.94L2.84 14.52C2.66 14.66 2.61 14.93 2.72 15.13L4.64 18.45C4.75 18.65 4.97 18.72 5.16 18.62L7.47 17.5C7.96 17.95 8.52 18.35 9.13 18.65L9.5 21.19C9.54 21.43 9.75 21.6 10 21.6H14C14.25 21.6 14.46 21.43 14.5 21.19L14.87 18.65C15.48 18.35 16.04 17.95 16.53 17.5L18.84 18.62C19.03 18.72 19.25 18.65 19.36 18.45L21.28 15.13C21.39 14.93 21.34 14.66 21.16 14.52L19.14 12.94ZM12 15.6C10.35 15.6 9 14.25 9 12.6C9 10.95 10.35 9.6 12 9.6C13.65 9.6 15 10.95 15 12.6C15 14.25 13.65 15.6 12 15.6Z" />
    </svg>
  ),

  Send: ({ size = 24, className = "" }: IconProps) => (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="currentColor"
      className={className}
    >
      <path d="M16.6915026,12.4744748 L3.50612381,13.2599618 C3.19218622,13.2599618 3.03521743,13.4170592 3.03521743,13.5741566 L1.15159189,20.0151496 C0.8376543,20.8006365 0.99,21.89 1.77946707,22.52 C2.41,22.99 3.50612381,23.1 4.13399899,22.8429026 L21.714504,14.0454487 C22.6563168,13.5741566 23.1272231,12.6315722 22.9702544,11.6889879 L4.13399899,1.16345869 C3.34915502,0.9 2.40734225,1.00636533 1.77946707,1.4776575 C0.994623095,2.10604706 0.837654326,3.0486314 1.15159189,3.99701575 L3.03521743,10.4380088 C3.03521743,10.5951061 3.19218622,10.7522035 3.50612381,10.7522035 L16.6915026,11.5376905 C16.6915026,11.5376905 17.1624089,11.5376905 17.1624089,12.0089827 C17.1624089,12.4744748 16.6915026,12.4744748 16.6915026,12.4744748 Z" />
    </svg>
  ),

  Back: ({ size = 24, className = "" }: IconProps) => (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="currentColor"
      className={className}
    >
      <path d="M20 11H7.83L13.42 5.41L12 4L4 12L12 20L13.41 18.59L7.83 13H20V11Z" />
    </svg>
  ),

  Menu: ({ size = 24, className = "" }: IconProps) => (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="currentColor"
      className={className}
    >
      <path d="M3 18H21V16H3V18ZM3 13H21V11H3V13ZM3 6V8H21V6H3Z" />
    </svg>
  ),

  Search: ({ size = 24, className = "" }: IconProps) => (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="currentColor"
      className={className}
    >
      <path d="M15.5 14H14.71L14.43 13.73C15.41 12.59 16 11.11 16 9.5C16 5.91 13.09 3 9.5 3C5.91 3 3 5.91 3 9.5C3 13.09 5.91 16 9.5 16C11.11 16 12.59 15.41 13.73 14.43L14 14.71V15.5L19 20.49L20.49 19L15.5 14ZM9.5 14C7.01 14 5 11.99 5 9.5C5 7.01 7.01 5 9.5 5C11.99 5 14 7.01 14 9.5C14 11.99 11.99 14 9.5 14Z" />
    </svg>
  ),

  Plus: ({ size = 24, className = "" }: IconProps) => (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="currentColor"
      className={className}
    >
      <path d="M19 13H13V19H11V13H5V11H11V5H13V11H19V13Z" />
    </svg>
  ),

  Close: ({ size = 24, className = "" }: IconProps) => (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="currentColor"
      className={className}
    >
      <path d="M19 6.41L17.59 5L12 10.59L6.41 5L5 6.41L10.59 12L5 17.59L6.41 19L12 13.41L17.59 19L19 17.59L13.41 12L19 6.41Z" />
    </svg>
  ),

  Home: ({ size = 24, className = "" }: IconProps) => (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="currentColor"
      className={className}
    >
      <path d="M10 20V14H14V20H19V12H22L12 3L2 12H5V20H10Z" />
    </svg>
  ),

  Phone: ({ size = 24, className = "" }: IconProps) => (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="currentColor"
      className={className}
    >
      <path d="M17 10.5V7C17 6.45 16.55 6 16 6H8C7.45 6 7 6.45 7 7V10.5C7 11.05 7.45 11.5 8 11.5H16C16.55 11.5 17 11.05 17 10.5ZM16 8V10H8V8H16ZM6 5H18C19.1 5 20 5.9 20 7V23H19V13H5V23H4V7C4 5.9 4.9 5 6 5ZM8 14H16V23H8V14Z" />
    </svg>
  ),

  Verified: ({ size = 24, className = "" }: IconProps) => (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="currentColor"
      className={className}
    >
      <path d="M12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2ZM10 17L5 12L6.41 10.59L10 14.17L17.59 6.58L19 8L10 17Z" />
    </svg>
  ),

  Heart: ({ size = 24, className = "" }: IconProps) => (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="currentColor"
      className={className}
    >
      <path d="M12 21.35L10.55 20.03C5.4 15.36 2 12.28 2 8.5C2 5.42 4.42 3 7.5 3C9.24 3 10.91 3.81 12 5.09C13.09 3.81 14.76 3 16.5 3C19.58 3 22 5.42 22 8.5C22 12.28 18.6 15.36 13.45 20.04L12 21.35Z" />
    </svg>
  ),

  Info: ({ size = 24, className = "" }: IconProps) => (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="currentColor"
      className={className}
    >
      <path d="M12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2ZM13 17H11V11H13V17ZM13 9H11V7H13V9Z" />
    </svg>
  ),

  ChevronRight: ({ size = 24, className = "" }: IconProps) => (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="currentColor"
      className={className}
    >
      <path d="M8.59 16.34L10 17.75L16.25 11.5L10 5.25L8.59 6.66L12.92 11L8.59 16.34Z" />
    </svg>
  ),

  Bell: ({ size = 24, className = "" }: IconProps) => (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="currentColor"
      className={className}
    >
      <path d="M12 22C13.1 22 14 21.1 14 20H10C10 21.1 10.89 22 12 22ZM18 16V11C18 7.93 16.36 5.36 13.5 4.68V4C13.5 3.22 12.88 2.5 12 2.5C11.12 2.5 10.5 3.22 10.5 4V4.68C7.64 5.36 6 7.92 6 11V16L4 18V19H20V18L18 16Z" />
    </svg>
  ),

  Eye: ({ size = 24, className = "" }: IconProps) => (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="currentColor"
      className={className}
    >
      <path d="M12 4.5C7 4.5 2.73 7.61 1 12C2.73 16.39 7 19.5 12 19.5C17 19.5 21.27 16.39 23 12C21.27 7.61 17 4.5 12 4.5ZM12 17C9.24 17 7 14.76 7 12C7 9.24 9.24 7 12 7C14.76 7 17 9.24 17 12C17 14.76 14.76 17 12 17ZM12 9C10.34 9 9 10.34 9 12C9 13.66 10.34 15 12 15C13.66 15 15 13.66 15 12C15 10.34 13.66 9 12 9Z" />
    </svg>
  ),

  EyeOff: ({ size = 24, className = "" }: IconProps) => (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="currentColor"
      className={className}
    >
      <path d="M11.83 9L15.23 12.4C15.48 11.84 15.62 11.21 15.62 10.5C15.62 8.92 14.54 7.63 13.05 7.63C12.37 7.63 11.74 7.77 11.17 8.02L11.83 9M7.5 6.6L8.63 7.74C7.25 8.82 6.38 10.4 6.38 12.13C6.38 15.35 8.76 17.93 11.81 17.93C13 17.93 14.13 17.61 15.08 17.05L16.24 18.2C15.02 18.82 13.63 19.25 12.13 19.25C6.92 19.25 2.62 15.95 1 11.05C2.25 8.58 4.34 6.74 7.5 6.6M2 4.27L4.28 6.55L4.73 7L7.73 10L7.73 10.02C7.73 10.02 7.27 9.5 7.17 9.38L5.59 7.81C3.86 8.9 2.36 10.4 1.27 12.13C2.62 15.95 6.92 19.25 12.13 19.25C13.05 19.25 13.96 19.16 14.86 19L20.73 25L22 23.73L3.27 2M12 7C11.4 7 10.86 7.08 10.36 7.24L13.72 10.6C13.88 10.1 13.96 9.56 13.96 9C13.96 7.9 13.1 7 12 7Z" />
    </svg>
  ),

  Copy: ({ size = 24, className = "" }: IconProps) => (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="currentColor"
      className={className}
    >
      <path d="M16 1H4C2.9 1 2 1.9 2 3V17H4V3H16V1ZM20 5H8C6.9 5 6 5.9 6 7V21C6 22.1 6.9 23 8 23H20C21.1 23 22 22.1 22 21V7C22 5.9 21.1 5 20 5ZM20 21H8V7H20V21Z" />
    </svg>
  ),
};

export type IconName = keyof typeof Icons;
