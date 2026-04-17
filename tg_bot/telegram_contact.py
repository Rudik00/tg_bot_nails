from html import escape


def escape_html_text(value: str | None) -> str:
    if value is None:
        return "-"
    return escape(str(value))


def build_contact_link_html(
    username: str | None,
    telegram_id: int | None,
    fallback_label: str,
) -> str:
    label = escape(fallback_label)
    if username:
        clean_username = username.lstrip("@")
        safe_username = escape(clean_username)
        return (
            f'<a href="https://t.me/{safe_username}">@{safe_username}</a>'
        )

    if telegram_id is not None:
        return f'<a href="tg://user?id={telegram_id}">{label}</a>'

    return label
