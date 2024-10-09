# Discord Economy Bot

A versatile Discord bot that provides users with various features such as an economy system, mini-games (like blackjack, slots, roulette), a work system, gambling games, and a slave/master system where users can enslave others and pay daily wages in coins.

## Key Features

- **Economy System**: Keep track of user balances, earn coins through work, and participate in various games to gain or lose coins.
- **Mini-games**:
  - **Coin Flip**: Bet coins on a coin flip and double your bet.
  - **Blackjack**: Play blackjack and try to beat the dealer.
  - **Slots**: Try your luck with a slot machine.
  - **Roulette**: Bet on numbers, colors, or odds/evens in a roulette game.
- **Work System**: Earn coins by typing sentences within a time limit. Three difficulty ilevels: Easy, Hard, and Death Sentence.
- **Slave/Master System**: Users can enslave others to pay daily wages. Masters can muzzle their slaves and even change their nicknames.
- **Stock Market**: Buy and sell stocks with fluctuating prices.
- **Lucky Wheel**: Spin the wheel for a chance to win various rewards.
- **Lottery**: Participate in a lottery and win coins based on ticket purchases.
- **Leaderboard**: View the server's coin balance rankings.

## Installation

### Prerequisites

- Python 3.8+
- `discord.py` library (v2.0+)
- `matplotlib` library
- Other dependencies listed in `requirements.txt`

### Instructions

1. Clone the repository:

   ```bash
   git clone https://github.com/SanityMinds/ByteBet.git

2. Navigate to the repository

   ```bash
   cd ByteBet

3. Install the dependencies

   ```bash
   pip install -r requirements.txt

4. Setup your bot token inside of the bot.py file

5. Run the bot

## commands

## economy commands

- /balance: shows your current avalible balance
- pay <user> <amount>: Pay another user a specific amount
- /leaderboard: view servers leaderboard

## mini game commands

- coin_flip: bet an amount on a coin flip
- blackjack <amount>: bet an amount on a game of blackjack
- slots <amount>: inset money into a slot machine
- roulette <amount> <bet>: bet on roulette
- work: Work to earn coins. Choose from easy, hard, or death sentence difficulties.

## enslavement commands

- enslave <user> <daily_payment>: ensalve a user for a daily payment of an amount of coins
- muzzle <user> <keywords>: muzzle a slave using keywords which they cannot say

## stock market commands

- stock_market: shows the current stock values
- portfolio: shows how many stocks you own
- buy_stock <symbol> <amount>: buy a stock amount

## fun commands

- blackmakret: visit the blackmarket
- lottery: partake in the global lottery
- shop: go shopping
- lucky_wheel: try your luck every 24 hours!

[Invite the bot to your server](https://discord.com/oauth2/authorize?client_id=1274514032044281866)
