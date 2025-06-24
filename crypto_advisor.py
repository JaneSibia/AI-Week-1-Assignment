import nltk
import json
from pycoingecko import CoinGeckoAPI
from datetime import datetime
import time
from colorama import Fore, Style, init
import re

# Initialize colorama for colored output
init()

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

class CryptoAdvisor:
    def __init__(self):
        self.name = "CryptoBuddy"
        # Initialize CoinGecko API
        self.cg = CoinGeckoAPI()
        
        # Static database for sustainability metrics, expanded with more coins
        self.crypto_db = {
            "bitcoin": {
                "market_cap": "high",
                "energy_use": "high",
                "sustainability_score": 3,
                "long_term_viability": 8,
                "tech_score": 9
            },
            "ethereum": {
                "market_cap": "high",
                "energy_use": "medium",
                "sustainability_score": 6,
                "long_term_viability": 9,
                "tech_score": 9
            },
            "cardano": {
                "market_cap": "high",
                "energy_use": "low",
                "sustainability_score": 8,
                "long_term_viability": 7,
                "tech_score": 8
            },
            "solana": {
                "market_cap": "high",
                "energy_use": "low",
                "sustainability_score": 7,
                "long_term_viability": 7,
                "tech_score": 8
            },
            "polkadot": {
                "market_cap": "medium",
                "energy_use": "low",
                "sustainability_score": 8,
                "long_term_viability": 8,
                "tech_score": 9
            },
            "ripple": {
                "market_cap": "high",
                "energy_use": "very low",
                "sustainability_score": 9,
                "long_term_viability": 6,
                "tech_score": 7
            },
            "dogecoin": {
                "market_cap": "medium",
                "energy_use": "medium",
                "sustainability_score": 4,
                "long_term_viability": 3,
                "tech_score": 5
            },
            "avalanche-2": {
                "market_cap": "high",
                "energy_use": "low",
                "sustainability_score": 8,
                "long_term_viability": 8,
                "tech_score": 8
            }
        }

    def get_live_prices(self):
        """Get real-time prices for all cryptocurrencies in our database"""
        try:
            # Dynamically fetch prices for all coins in the DB
            prices = self.cg.get_price(
                ids=list(self.crypto_db.keys()),
                vs_currencies='usd',
                include_24h_change=True
            )
            return prices
        except Exception as e:
            print(f"{Fore.RED}Error fetching prices: {e}{Style.RESET_ALL}")
            return None

    def analyze_price_trend(self, change_24h):
        """Analyze if price trend is rising, falling, or stable"""
        if change_24h > 5:
            return "rising strongly"
        elif change_24h > 2:
            return "rising"
        elif change_24h < -5:
            return "falling sharply"
        elif change_24h < -2:
            return "falling"
        else:
            return "stable"

    def get_most_sustainable(self):
        """Find the most sustainable cryptocurrency"""
        return max(self.crypto_db.items(), 
                  key=lambda x: x[1]['sustainability_score'])

    def get_best_tech(self):
        """Find the coin with the best technology score."""
        return max(self.crypto_db.items(), key=lambda x: x[1]['tech_score'])

    def get_low_energy_coins(self):
        """Find coins with low energy use."""
        return [coin for coin, data in self.crypto_db.items() if data['energy_use'] in ['low', 'very low']]

    def get_coin_details(self, coin_name, prices):
        """Get all details for a specific coin."""
        display_name = coin_name.replace('-2', '').title()
        if coin_name not in self.crypto_db:
            return f"Sorry, I don't have detailed data for {display_name}."

        details = self.crypto_db[coin_name]
        price_data = prices.get(coin_name, {})
        price = price_data.get('usd', 'N/A')
        change = price_data.get('usd_24h_change', 0)
        trend = self.analyze_price_trend(change)

        response = f"--- Details for {display_name} ---\n"
        response += f"Price: ${price:,.2f}\n" if isinstance(price, (int, float)) else f"Price: {price}\n"
        response += f"24h Trend: {trend} ({change:+.1f}%)\n"
        response += f"Market Cap: {details['market_cap'].title()}\n"
        response += f"Energy Use: {details['energy_use'].title()}\n"
        response += f"Sustainability Score: {details['sustainability_score']}/10\n"
        response += f"Tech Score: {details['tech_score']}/10\n"
        response += f"Long-term Viability: {details['long_term_viability']}/10\n"
        return response

    def get_best_long_term(self):
        """Find the best long-term investment based on multiple factors"""
        scored_coins = {}
        for coin, data in self.crypto_db.items():
            score = (data['sustainability_score'] + 
                    data['long_term_viability'] + 
                    data['tech_score']) / 3
            scored_coins[coin] = score
        return max(scored_coins.items(), key=lambda x: x[1])

    def process_query(self, user_input):
        """Process user input and return appropriate response"""
        user_input = user_input.lower()
        
        # Get current prices for context
        prices = self.get_live_prices()
        
        if not prices:
            return "I'm having trouble getting current market data. Let me provide advice based on historical analysis."

        # Check for specific coin details query first
        matched_coin = None
        for coin in self.crypto_db.keys():
            if re.search(r'\b' + re.escape(coin) + r'\b', user_input):
                matched_coin = coin
                break
        
        if matched_coin and any(keyword in user_input for keyword in ['about', 'details', 'info', 'what is']):
             return self.get_coin_details(matched_coin, prices)

        if any(word in user_input for word in ['sustainable', 'green', 'eco']):
            best_coin, _ = self.get_most_sustainable()
            return (f"Based on sustainability metrics, {best_coin.title()} is your best bet! 🌱\n"
                   f"It has a sustainability score of {self.crypto_db[best_coin]['sustainability_score']}/10 "
                   f"and {self.crypto_db[best_coin]['energy_use']} energy usage.")

        elif any(word in user_input for word in ['tech', 'technology']):
            best_coin, data = self.get_best_tech()
            display_name = best_coin.replace('-2', '').title()
            return f"For the best technology, look at {display_name}! 💻 It has a tech score of {data['tech_score']}/10."

        elif any(word in user_input for word in ['low energy', 'energy use']):
            low_energy_coins = self.get_low_energy_coins()
            formatted_coins = ', '.join([c.replace('-2', '').title() for c in low_energy_coins])
            return f"Looking for low energy consumption? Check these out: 🌱\n- {formatted_coins}"

        elif any(word in user_input for word in ['profit', 'profitable']):
            profitable_coins = []
            for coin, data in prices.items():
                trend = self.analyze_price_trend(data.get('usd_24h_change', 0))
                market_cap = self.crypto_db.get(coin, {}).get('market_cap', 'low')
                if "rising" in trend and market_cap == "high":
                    profitable_coins.append(coin.replace('-2', '').title())
            
            if profitable_coins:
                return (f"Based on current trends and market cap, these coins look profitable: 🚀\n"
                       f"- {', '.join(profitable_coins)}")
            else:
                return "No coins are currently meeting the criteria for high profitability (rising trend + high market cap)."

        elif any(word in user_input for word in ['trend', 'trending', 'price']):
            response = "Here's the current price trends:\n"
            for coin, data in prices.items():
                price = data.get('usd', 0.0)
                change = data.get('usd_24h_change', 0.0)
                trend = self.analyze_price_trend(change)
                display_name = coin.replace('-2', '').title()
                response += f"{display_name}: ${price:,.2f} ({change:+.2f}% - {trend})\n"
            return response

        elif any(word in user_input for word in ['long term', 'long-term', 'future']):
            best_coin, score = self.get_best_long_term()
            return (f"For long-term investment potential, I recommend {best_coin.title()}! 📈\n"
                   f"It scores well in sustainability ({self.crypto_db[best_coin]['sustainability_score']}/10), "
                   f"long-term viability ({self.crypto_db[best_coin]['long_term_viability']}/10), "
                   f"and technical fundamentals ({self.crypto_db[best_coin]['tech_score']}/10).")

        elif 'help' in user_input or 'what' in user_input:
            return """I can help you with:
1. Cryptocurrency price trends ("Show me trending coins")
2. Sustainability analysis ("Which crypto is most sustainable?")
3. Long-term investment potential ("Best coin for long-term?")
4. Profitability analysis ("Which coins are profitable?")
5. Technology scores ("Which coin has the best tech?")
6. Low-energy coins ("Show me low-energy coins")
7. Specific coin details ("Tell me about Bitcoin")
8. Current prices ("Show me current prices")"""

        elif matched_coin:
            return self.get_coin_details(matched_coin, prices)

        else:
            return ("I'm not sure what you're asking. Try asking about:\n"
                   "- Price trends\n"
                   "- Sustainability\n"
                   "- Long-term potential\n"
                   "- Profitability\n"
                   "- Technology\n"
                   "- Low-energy coins\n"
                   "- Specific coin details\n"
                   "Or type 'help' for more options!")

    def display_initial_summary(self):
        print(f"{Fore.CYAN}Fetching initial market data...{Style.RESET_ALL}")
        prices = self.get_live_prices()
        if not prices:
            print(f"{Fore.YELLOW}Could not fetch live market data. Please check your connection.{Style.RESET_ALL}")
            return

        print(f"{Fore.YELLOW}--- Crypto Market Snapshot ---{Style.RESET_ALL}")
        print(f"{'Coin':<12} | {'Price (USD)':<15} | {'24h Change':<12} | {'Trend'}")
        print("-" * 60)

        for coin, data in prices.items():
            price = data.get('usd', 0)
            change = data.get('usd_24h_change', 0)
            trend = self.analyze_price_trend(change)
            
            if "rising" in trend:
                color = Fore.GREEN
            elif "falling" in trend:
                color = Fore.RED
            else:
                color = Fore.WHITE
            
            # Handle coins with different IDs in API, like avalanche-2
            display_name = coin.replace('-2', '').title()
            print(f"{display_name:<12} | ${price:<14,.2f} | {color}{change:+.1f}%{Style.RESET_ALL:<12} | {color}{trend}{Style.RESET_ALL}")
        print("-" * 60)
        
        best_sustainable_coin, _ = self.get_most_sustainable()
        print(f"🌱 {Fore.CYAN}Top Sustainable Pick:{Style.RESET_ALL} {best_sustainable_coin.title()}")
        print("\n")

def main():
    advisor = CryptoAdvisor()
    
    # Welcome message
    print(f"{Fore.CYAN}Welcome to {advisor.name}! 🤖 Your AI-Powered Crypto Investment Advisor!{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Disclaimer: This is for educational purposes only. Always do your own research!{Style.RESET_ALL}\n")
    
    advisor.display_initial_summary()

    print(f"How can I help you today? Try asking one of these questions:")
    print(f"{Fore.YELLOW}- 'Which crypto is trending up?'")
    print(f"- 'What's the most sustainable coin?'")
    print(f"- 'What do you recommend for long-term growth?'")
    print(f"- 'Which coins look profitable?'")
    print(f"- 'Tell me about Ethereum'")
    print(f"- 'Which coin has the best technology?'")
    print(f"- 'Which coins use low energy?'")
    print(f"- 'Show me all current prices'{Style.RESET_ALL}")
    print(" (Type 'exit' to quit)")

    while True:
        try:
            user_input = input(f"\n{Fore.GREEN}You:{Style.RESET_ALL} ").strip()
            
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print(f"\n{Fore.CYAN}{advisor.name}: Goodbye! Happy investing! 👋{Style.RESET_ALL}")
                break
                
            if not user_input:
                continue
            
            response = advisor.process_query(user_input)
            print(f"\n{Fore.BLUE}{advisor.name}:{Style.RESET_ALL} {response}")

        except KeyboardInterrupt:
            print(f"\n\n{Fore.CYAN}{advisor.name}: Goodbye! Happy investing! 👋{Style.RESET_ALL}")
            break
        except Exception as e:
            print(f"{Fore.RED}An error occurred: {e}{Style.RESET_ALL}")
            print("Please try again!")

if __name__ == "__main__":
    main() 