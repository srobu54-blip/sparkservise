// SPARK — Edge Function: новая заявка -> сообщение в Telegram.
// Вызывается Supabase Database Webhook на INSERT в public.leads.
// Секреты (Project Settings -> Edge Functions -> Secrets, либо `supabase secrets set`):
//   TELEGRAM_BOT_TOKEN  — токен бота от @BotFather
//   TELEGRAM_CHAT_ID    — id чата/канала/группы, куда слать (можно узнать у @userinfobot)
//   WEBHOOK_SECRET      — произвольная строка; ТОТ ЖЕ секрет добавить в вебхук как
//                         HTTP-заголовок «x-webhook-secret» (защита от чужих вызовов функции)
// Функция публичная по URL, поэтому проверяем секретный заголовок — иначе кто угодно
// мог бы слать тебе фейковые «заявки» в Telegram.

const TG_TOKEN = Deno.env.get("TELEGRAM_BOT_TOKEN") ?? "";
const TG_CHAT = Deno.env.get("TELEGRAM_CHAT_ID") ?? "";
const SECRET = Deno.env.get("WEBHOOK_SECRET") ?? "";

function esc(s: unknown): string {
  return String(s ?? "").replace(/[<>&]/g, (c) => ({ "<": "&lt;", ">": "&gt;", "&": "&amp;" }[c] as string));
}

function fmtDate(iso: string | null): string {
  try {
    return new Intl.DateTimeFormat("ru-UA", {
      timeZone: "Europe/Kyiv", day: "2-digit", month: "2-digit", year: "numeric",
      hour: "2-digit", minute: "2-digit",
    }).format(iso ? new Date(iso) : new Date());
  } catch {
    return iso ?? "";
  }
}

const SRC: Record<string, string> = {
  exit_popup: "Exit-попап", modal_callback: "Модалка «Записаться»",
  inline_form: "Форма на странице", unknown: "Форма",
};

Deno.serve(async (req) => {
  if (req.method !== "POST") return new Response("Method not allowed", { status: 405 });

  // защита: без верного секрета — 401 (функция публична по URL)
  if (!SECRET || req.headers.get("x-webhook-secret") !== SECRET) {
    return new Response("Unauthorized", { status: 401 });
  }
  if (!TG_TOKEN || !TG_CHAT) {
    return new Response("Telegram not configured", { status: 500 });
  }

  let rec: Record<string, unknown> = {};
  try {
    const body = await req.json();
    rec = (body?.record ?? body) as Record<string, unknown>; // формат Supabase DB Webhook: {type, record, ...}
  } catch {
    return new Response("Bad payload", { status: 400 });
  }

  const lines = [
    "🔔 <b>Новая заявка — SPARK</b>",
    `📞 <b>${esc(rec.phone)}</b>`,
    rec.name ? `👤 ${esc(rec.name)}` : "",
    rec.service ? `🛠 ${esc(rec.service)}` : "",
    `🌐 ${esc(SRC[String(rec.source)] ?? rec.source)}${rec.lang ? " · " + esc(rec.lang) : ""}`,
    rec.page_url ? `🔗 ${esc(rec.page_url)}` : "",
    `🕒 ${esc(fmtDate((rec.created_at as string) ?? null))}`,
  ].filter(Boolean);

  const tg = await fetch(`https://api.telegram.org/bot${TG_TOKEN}/sendMessage`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      chat_id: TG_CHAT, text: lines.join("\n"),
      parse_mode: "HTML", disable_web_page_preview: true,
    }),
  });

  if (!tg.ok) {
    const err = await tg.text();
    return new Response(`Telegram error: ${err}`, { status: 502 });
  }
  return new Response(JSON.stringify({ ok: true }), {
    headers: { "Content-Type": "application/json" },
  });
});
