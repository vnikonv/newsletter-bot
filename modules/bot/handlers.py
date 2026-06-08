from telegram.ext import (
    CommandHandler,
    MessageHandler,
    filters,
)

from modules.bot.commands import (
    start_command,
    send_command,
    regenerate_command,
    change_command,
    cancel_command,
    handle_input,
    see_email,
)


def register_handlers(app):
    app.add_handler(
        CommandHandler(
            "start",
            start_command
        )
    )

    app.add_handler(
        CommandHandler(
            "send",
            send_command
        )
    )

    app.add_handler(
        CommandHandler(
            "regenerate",
            regenerate_command
        )
    )

    app.add_handler(
        CommandHandler(
            "change",
            change_command
        )
    )

    app.add_handler(
        CommandHandler(
            "cancel",
            cancel_command
        )
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_input
        )
    )

    app.add_handler(
        CommandHandler(
            "email",
            see_email
        )
    )
