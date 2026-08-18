import { Context } from "telegraf";
import { UserService } from "../services/userService";
import { NumberService } from "../services/numberService";

export const handleStart = async (ctx: Context) => {
  const user = ctx.from;
  if (!user) return;

  await UserService.getOrCreateTelegramUser(
    user.id,
    user.first_name,
    user.username,
    user.last_name
  );

  await ctx.reply(
    "🎉 *Welcome to CrolGram!*\n\n" +
      "Premium messaging & collectibles platform\n\n" +
      "What would you like to do?",
    {
      parse_mode: "Markdown",
      reply_markup: {
        inline_keyboard: [
          [
            {
              text: "📱 Get Free Number",
              callback_data: "get_free_number",
            },
          ],
          [
            {
              text: "💎 Buy Beautiful Number",
              callback_data: "buy_premium_number",
            },
          ],
          [
            {
              text: "📋 My Numbers",
              callback_data: "my_numbers",
            },
          ],
          [
            {
              text: "⭐ Get Free CG Stars",
              callback_data: "free_stars",
            },
          ],
          [
            {
              text: "💳 Buy CG Stars",
              callback_data: "buy_stars",
            },
          ],
          [
            {
              text: "🔐 Get Verification",
              callback_data: "get_verification",
            },
          ],
          [
            {
              text: "🌐 Open CrolGram Web",
              url: "https://crolg.app",
            },
          ],
        ],
      },
    }
  );
};

export const handleGetFreeNumber = async (ctx: Context) => {
  const user = ctx.from;
  if (!user) return;

  const countries = await NumberService.getCountries();

  if (countries.length === 0) {
    await ctx.answerCallbackQuery("No countries available");
    return;
  }

  const keyboard = countries.map((country) => [
    {
      text: `${country.flag} ${country.name}`,
      callback_data: `select_country_free_${country.code}`,
    },
  ]);

  // Add back button
  keyboard.push([
    {
      text: "⬅️ Back",
      callback_data: "back_to_menu",
    },
  ]);

  await ctx.editMessageText("🌍 *Select Country*\n\nChoose where to get your free number:", {
    parse_mode: "Markdown",
    reply_markup: {
      inline_keyboard: keyboard,
    },
  });
};

export const handleSelectCountryFree = async (
  ctx: Context,
  countryCode: string
) => {
  const numbers = await NumberService.getFreeNumbers(countryCode);

  if (numbers.length === 0) {
    await ctx.answerCallbackQuery("No free numbers available for this country");
    return;
  }

  const keyboard = numbers.map((number) => [
    {
      text: number.formattedNumber,
      callback_data: `assign_number_${number.numberId}`,
    },
  ]);

  // Add back button
  keyboard.push([
    {
      text: "⬅️ Back",
      callback_data: "get_free_number",
    },
  ]);

  await ctx.editMessageText("📱 *Available Numbers*\n\nSelect a number:", {
    parse_mode: "Markdown",
    reply_markup: {
      inline_keyboard: keyboard,
    },
  });
};

export const handleMyNumbers = async (ctx: Context) => {
  const user = ctx.from;
  if (!user) return;

  const telegramUser = await UserService.getOrCreateTelegramUser(
    user.id,
    user.first_name,
    user.username,
    user.last_name
  );

  if (!telegramUser.linkedCrolGramUid) {
    await ctx.editMessageText(
      "🔗 *Link CrolGram Account*\n\n" +
        "You haven't linked your CrolGram account yet.\n\n" +
        "Visit CrolGram Web to create an account and link it.",
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
    return;
  }

  const numbers = await NumberService.getUserNumbers(
    telegramUser.linkedCrolGramUid
  );

  if (numbers.length === 0) {
    await ctx.editMessageText(
      "📭 *No Numbers*\n\n" +
        "You don't have any CrolGram numbers yet.\n\n" +
        "Get a free number or buy a beautiful one!",
      {
        parse_mode: "Markdown",
        reply_markup: {
          inline_keyboard: [
            [
              {
                text: "📱 Get Free Number",
                callback_data: "get_free_number",
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
    return;
  }

  const numbersList = numbers
    .map(
      (n) => `${n.country} • *${n.formattedNumber}*\n${n.type === "free" ? "✨ Free" : "💎 Premium"}`
    )
    .join("\n\n");

  await ctx.editMessageText(
    "📱 *My CrolGram Numbers*\n\n" + numbersList,
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
};

export const handleFreeStars = async (ctx: Context) => {
  const user = ctx.from;
  if (!user) return;

  const telegramUser = await UserService.getOrCreateTelegramUser(
    user.id,
    user.first_name,
    user.username,
    user.last_name
  );

  if (!telegramUser.linkedCrolGramUid) {
    await ctx.answerCallbackQuery("Link CrolGram account first");
    return;
  }

  // TODO: Implement free stars logic via Cloud Function
  await ctx.answerCallbackQuery("✨ Free stars claim coming soon!");
};

export const handleBuyStars = async (ctx: Context) => {
  await ctx.editMessageText(
    "💳 *Buy CG Stars*\n\n" +
      "Choose payment method:\n\n" +
      "_Payment options coming soon_",
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
};

export const handleBackToMenu = async (ctx: Context) => {
  await handleStart(ctx);
};
