import "dotenv/config";
import { Telegraf } from "telegraf";
import { Context } from "telegraf";
import {
  handleStart,
  handleGetFreeNumber,
  handleSelectCountryFree,
  handleMyNumbers,
  handleFreeStars,
  handleBuyStars,
  handleBackToMenu,
} from "./handlers/commands";

const bot = new Telegraf(process.env.TELEGRAM_BOT_TOKEN || "");

// Logging middleware
bot.use(async (ctx, next) => {
  console.log(`[${new Date().toISOString()}] Update:`, {
    from: ctx.from?.username || ctx.from?.id,
    type: ctx.updateType,
    data: ctx.updateSubTypes,
  });
  await next();
});

// Error handling
bot.catch((err, ctx) => {
  console.error(`Error for ${ctx.updateType}:`, err);
  ctx
    .reply("❌ An error occurred. Please try again.")
    .catch((e) => console.error("Failed to send error message:", e));
});

// Commands
bot.command("start", handleStart);
bot.command("help", async (ctx) => {
  await ctx.reply(
    "🎉 *CrolGram Bot Help*\n\n" +
      "/start - Main menu\n" +
      "/help - This message\n\n" +
      "Use buttons to navigate and perform actions.",
    {
      parse_mode: "Markdown",
    }
  );
});

// Callback queries (button presses)
bot.action("back_to_menu", handleBackToMenu);
bot.action("get_free_number", handleGetFreeNumber);
bot.action(/^select_country_free_(.+)$/, (ctx) => {
  const match = (ctx as any).match;
  const countryCode = match[1];
  return handleSelectCountryFree(ctx, countryCode);
});

bot.action(/^assign_number_(.+)$/, async (ctx) => {
  const match = (ctx as any).match;
  const numberId = match[1];

  const user = ctx.from;
  if (!user) {
    await ctx.answerCallbackQuery("User not found");
    return;
  }

  // TODO: Link check and assign via Cloud Function
  await ctx.answerCallbackQuery("✅ Number assigned! Check CrolGram Web.");
  await handleBackToMenu(ctx);
});

bot.action("my_numbers", handleMyNumbers);
bot.action("buy_premium_number", async (ctx) => {
  await ctx.editMessageText(
    "💎 *Beautiful Numbers*\n\n" +
      "Premium & special numbers coming soon!",
    {
      parse_mode: "Markdown",
      reply_markup: {
        inline_keyboard: [
          [
            {
              text: "⬅️ Back",
              callback_data: "back_to_menu",
            },
          ],
        ],
      },
    }
  );
});

bot.action("free_stars", handleFreeStars);
bot.action("buy_stars", handleBuyStars);
bot.action("get_verification", async (ctx) => {
  await ctx.editMessageText(
    "🔐 *CrolGram Verification*\n\n" +
      "Apply for verification badge on CrolGram Web.",
    {
      parse_mode: "Markdown",
      reply_markup: {
        inline_keyboard: [
          [
            {
              text: "Open CrolGram",
              url: "https://crolg.app",
            },
          ],
          [
            {
              text: "⬅️ Back",
              callback_data: "back_to_menu",
            },
          ],
        ],
      },
    }
  );
});

// Fallback
bot.on("message", async (ctx) => {
  await ctx.reply("👋 Type /start to get started or use the menu buttons.");
});

// Launch
const startBot = async () => {
  try {
    console.log("🤖 CrolGram Bot starting...");
    await bot.launch();
    console.log("✅ Bot is running");
  } catch (error) {
    console.error("❌ Bot launch failed:", error);
    process.exit(1);
  }
};

startBot();

// Graceful shutdown
process.once("SIGINT", () => {
  console.log("Shutting down...");
  bot.stop("SIGINT");
});
process.once("SIGTERM", () => {
  console.log("Shutting down...");
  bot.stop("SIGTERM");
});

export default bot;
