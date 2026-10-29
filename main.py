"""Stop slash-prefixed QQ Official group messages from reaching the LLM."""

from astrbot.api import logger
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.message_components import Plain
from astrbot.api.provider import ProviderRequest
from astrbot.api.star import Context, Star


class SlashGuard(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    @staticmethod
    def _starts_with_slash(event: AstrMessageEvent) -> bool:
        """Check raw content because the wake-up prefix may be stripped later."""
        candidates = []
        message_obj = event.message_obj

        if message_obj is not None:
            # The message chain generally retains the original command prefix.
            parts = [
                item.text
                for item in (getattr(message_obj, "message", None) or [])
                if isinstance(item, Plain) and item.text
            ]
            if parts:
                candidates.append("".join(parts))

            # QQ Official adapters may expose the original payload as a dict.
            raw = getattr(message_obj, "raw_message", None)
            if isinstance(raw, dict):
                content = raw.get("content")
                if isinstance(content, str):
                    candidates.append(content)

            candidates.append(getattr(message_obj, "message_str", ""))

        candidates.append(event.message_str)
        return any(
            isinstance(text, str) and text.lstrip().startswith("/")
            for text in candidates
        )

    @filter.on_llm_request()
    async def block_slash_llm(
        self, event: AstrMessageEvent, req: ProviderRequest
    ) -> None:
        # Only intercept group chats on QQ Official (WebSocket / Webhook).
        if event.get_platform_name() not in ("qq_official", "qq_official_webhook"):
            return
        if event.is_private_chat():
            return

        # Built-in commands are normally handled before the LLM request hook.
        if self._starts_with_slash(event):
            logger.info("[SlashGuard] Blocked slash-prefixed LLM request")
            event.stop_event()
