import logging
import datetime
from telegram import Update
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from config import BOT_TOKEN
from dotenv import load_dotenv
from telegram.ext import (
    ContextTypes,
    filters,
    ApplicationBuilder,
    Application,
    CommandHandler,
    CallbackContext,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler, )

# Get environment variables
load_dotenv()

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Define conversation states
GET_COST, GET_PEOPLE, GET_NAMES = range(3)

# Store user data
user_data = {}

# Function to start the conversation and ask for the cost
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Welcome! Please enter the total cost of the item:")
    return GET_COST  # Move to the GET_COST state

# Function to get the cost
async def get_cost(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    try:
        cost = round(float(text), 2)
        user_data['cost'] = cost
        await update.message.reply_text(f"The total cost is {cost}. Now, how many people are splitting the cost?")
        return GET_PEOPLE  # Move to the GET_PEOPLE state
    except ValueError:
        await update.message.reply_text("Please enter a valid number for the cost.")
        return GET_COST  # Stay in the GET_COST state

# Function to get the number of people
async def get_people(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    try:
        people = int(text)
        if people > 0:
            user_data['people_count'] = people
            await update.message.reply_text(f"The cost per person is {user_data['cost'] / people:.2f}. Write out the names of all the people who are involved:")
            return GET_NAMES  # Move to the GET_NAMES state
        else:
            await update.message.reply_text("Please enter a valid number of people.")
            return GET_PEOPLE  # Stay in the GET_PEOPLE state
    except ValueError:
        await update.message.reply_text("Please enter a valid number of people.")
        return GET_PEOPLE  # Stay in the GET_PEOPLE state

# Function to get the names of all people involved
async def get_names(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    names = [name.strip() for name in text.split(",")] if "," in text else text.split()

    # Check if the number of names matches the number of people
    if len(names) == user_data['people_count']:
        user_data['people'] = names
        formatted_names = "\n".join(names)
        keyboard = [  
               [InlineKeyboardButton("Paid!", callback_data='count_out')] ]
        reply_markup = InlineKeyboardMarkup(keyboard) 
        await update.message.reply_text(f"Total cost of {user_data['cost']} is split amongst {user_data['people_count']} at ${user_data['cost'] / user_data['people_count']:.2f} each. Names of the people involved:\n{formatted_names}\nPress the button to add your name!", reply_markup= reply_markup)
        return ConversationHandler.END  # End the conversation
    else:
        await update.message.reply_text(f"Please enter exactly {user_data['people_count']} names.")
        return GET_NAMES  # Stay in the GET_NAMES state

# Function to cancel the conversation
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("The process has been canceled.")
    return ConversationHandler.END

# keyboard button
async def button(update: Update, context): 
    query = update.callback_query 
    user_name = "@" + query.from_user.username
    action = query.data 
 
    await query.answer() 

    # Handle "Count me out!" 
    

    keyboard = [[InlineKeyboardButton("Count me in!", callback_data= 'count_in')] ] 
     
    reply_markup = InlineKeyboardMarkup(keyboard) 

    if action == 'count_out' and user_name in user_data['people']: 
        user_data.get('people').remove(user_name)

 
    await query.edit_message_text( 
        text=f"Total cost of {user_data['cost']} is split amongst {user_data['people_count']} at ${user_data['cost'] / user_data['people_count']:.2f} each. Names of the people involved:\n{'\n'.join(user_data.get('people'))}\nPress the button to add your name!", 
        reply_markup=reply_markup 
    )


def main():
    # Create the application and add handlers
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Define the conversation handler with states and functions
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],  # Starts the conversation
        states={
            GET_COST: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_cost)],
            GET_PEOPLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_people)],
            GET_NAMES: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_names)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]  # Handle cancel command
    )

    # Add the conversation handler to the application
    application.add_handler(conv_handler)

    # Add handler for buttons
    application.add_handler(CallbackQueryHandler(button))

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()
