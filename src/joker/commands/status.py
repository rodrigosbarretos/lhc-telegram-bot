import httpx
import parsel
from telegram.constants import ParseMode

from joker import settings


async def status(update, context):
    response = httpx.get("https://lhc.net.br/spacenet.json?whois").json()
    status = f'aberto com {response["n_known_macs"]} pessoas associadas' if response["n_known_macs"] else 'fechado'
    if response["n_unknown_macs"]:
        desconhecidos = f'mais {response["n_unknown_macs"]} maritacas' if response["n_unknown_macs"] > 1 else 'mais uma maritaca solitária'
    else:
        desconhecidos = ''

    await context.bot.send_message(
        update.message.chat_id,
        text=f"O LHC está {status}{desconhecidos} desde {response['last_change']}",
    )

async def quem(update, context):
    await context.bot.send_message(
        update.message.chat_id,
        text="Eu não faço a menor ideia quem está no LHC agora.",
    )


def _get_status_infra():
    response = httpx.get(settings.MONTASTIC_RSS_URL)
    rss = parsel.Selector(response.text)
    statuses = rss.css("item title::text").getall()

    status_emojis = {
        "[OK]": "🟢",
        "[Alert]": "🔴",
    }
    formatted_statuses = []
    for status in sorted(statuses):
        condition, _ = status.split(" - ")
        emoji = status_emojis.get(condition, "🟡")
        formatted_statuses.append(status.replace(condition, emoji))

    if formatted_statuses:
        status_msg = "\n".join(formatted_statuses)
        return f"Status da infraestrutura do LHC:\n\n{status_msg}"

    return "🔴 Não foi possível obter o status da infraestrutura do LHC."


async def status_infra(update, context):
    await context.bot.send_message(
        update.message.chat_id,
        text=_get_status_infra(),
        disable_web_page_preview=True,
        parse_mode=ParseMode.MARKDOWN,
    )


async def recurring_status_infra(context):
    await context.bot.send_message(
        settings.LHC_CHAT_ID,
        text=_get_status_infra(),
        disable_web_page_preview=True,
        parse_mode=ParseMode.MARKDOWN,
    )
