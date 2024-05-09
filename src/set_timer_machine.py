import logging
from machine import Machine
from telegram.ext import ConversationHandler, CallbackContext
from telegram import Update

logger = logging.getLogger("set_timer_machine")


def set_timer_machine(machines: dict[str, dict[str, Machine]]):
    async def set_timer(update: Update, context: CallbackContext):
        chat_id = update.effective_message.chat_id
        query = update.callback_query
        await query.answer()

        machine_id = query.data.split("|")[1].strip()
        house_id = context.chat_data.get("house")
        machine = machines.get(house_id).get(machine_id)

        if machine == None:
            raise Exception(f"Unknown machine {machine_id}")

        machine_name = machine.get_name()

        if not (machine.start_machine(update.effective_message.chat.username, chat_id)):
            text = f"{machine_name} is currently in use. Please come back again later!"
            await query.edit_message_text(text=text)
        else:
            logger.info(
                f"{update.effective_user.username} started {house_id} {machine_name}"
            )
            text = f"Timer Set for {Machine.COMPLETION_TIME // 60}mins for {machine_name}. Please come back again!"
            await query.edit_message_text(text=text)

        return ConversationHandler.END

    return set_timer
