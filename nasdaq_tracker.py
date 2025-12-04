"""
NASDAQ Daily Movement Tracker
Tracks NASDAQ index movement by comparing current day prices with previous day prices.
"""

import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd


def get_nasdaq_data(symbol='^IXIC', period='5d'):
    """
    Fetch NASDAQ data using yfinance.
    
    Args:
        symbol: Stock/index symbol (default: ^IXIC for NASDAQ Composite)
        period: Period to fetch data for (default: 5d for 5 days)
    
    Returns:
        DataFrame with historical data
    """
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period=period)
        return data
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None


def calculate_daily_movement(data):
    """
    Calculate daily movement based on previous day's closing price.
    
    Args:
        data: DataFrame with historical price data
    
    Returns:
        Dictionary with movement details
    """
    if data is None or len(data) < 2:
        return None
    
    # Get the last two days of data
    recent_data = data.tail(2)
    
    # Previous day (second to last)
    prev_day = recent_data.iloc[-2]
    prev_close = prev_day['Close']
    prev_date = prev_day.name.date()
    
    # Current day (last)
    current_day = recent_data.iloc[-1]
    current_open = current_day['Open']
    current_close = current_day['Close']
    current_high = current_day['High']
    current_low = current_day['Low']
    current_date = current_day.name.date()
    
    # Calculate changes
    price_change = current_close - prev_close
    percent_change = (price_change / prev_close) * 100
    
    # Calculate intraday change
    intraday_change = current_close - current_open
    intraday_percent = (intraday_change / current_open) * 100
    
    # Calculate high/low from previous close
    high_from_prev = current_high - prev_close
    low_from_prev = current_low - prev_close
    
    return {
        'previous_date': prev_date,
        'previous_close': prev_close,
        'current_date': current_date,
        'current_open': current_open,
        'current_close': current_close,
        'current_high': current_high,
        'current_low': current_low,
        'price_change': price_change,
        'percent_change': percent_change,
        'intraday_change': intraday_change,
        'intraday_percent': intraday_percent,
        'high_from_prev': high_from_prev,
        'low_from_prev': low_from_prev,
        'range': current_high - current_low
    }


def display_movement(movement_data):
    """
    Display the movement data in a formatted way.
    
    Args:
        movement_data: Dictionary with movement details
    """
    if movement_data is None:
        print("Unable to calculate movement. Insufficient data.")
        return
    
    print("=" * 60)
    print("NASDAQ DAILY MOVEMENT TRACKER")
    print("=" * 60)
    print(f"\nPrevious Day: {movement_data['previous_date']}")
    print(f"Previous Close: ${movement_data['previous_close']:,.2f}")
    print(f"\nCurrent Day: {movement_data['current_date']}")
    print(f"Open:  ${movement_data['current_open']:,.2f}")
    print(f"High:  ${movement_data['current_high']:,.2f}")
    print(f"Low:   ${movement_data['current_low']:,.2f}")
    print(f"Close: ${movement_data['current_close']:,.2f}")
    print(f"Range: ${movement_data['range']:,.2f}")
    
    print("\n" + "-" * 60)
    print("MOVEMENT FROM PREVIOUS DAY CLOSE:")
    print("-" * 60)
    
    change_symbol = "▲" if movement_data['price_change'] >= 0 else "▼"
    color_indicator = "GREEN" if movement_data['price_change'] >= 0 else "RED"
    
    print(f"Price Change: {change_symbol} ${abs(movement_data['price_change']):,.2f}")
    print(f"Percent Change: {change_symbol} {abs(movement_data['percent_change']):.2f}%")
    print(f"Status: {color_indicator}")
    
    print("\n" + "-" * 60)
    print("INTRADAY MOVEMENT:")
    print("-" * 60)
    
    intraday_symbol = "▲" if movement_data['intraday_change'] >= 0 else "▼"
    intraday_color = "GREEN" if movement_data['intraday_change'] >= 0 else "RED"
    
    print(f"Open to Close: {intraday_symbol} ${abs(movement_data['intraday_change']):,.2f}")
    print(f"Open to Close %: {intraday_symbol} {abs(movement_data['intraday_percent']):.2f}%")
    print(f"Status: {intraday_color}")
    
    print("\n" + "-" * 60)
    print("FROM PREVIOUS CLOSE:")
    print("-" * 60)
    print(f"High: +${movement_data['high_from_prev']:,.2f}")
    print(f"Low:  ${movement_data['low_from_prev']:,.2f}")
    
    print("=" * 60)


def track_nasdaq(symbol='^IXIC'):
    """
    Main function to track NASDAQ movement.
    
    Args:
        symbol: Stock/index symbol (default: ^IXIC for NASDAQ Composite)
    """
    print(f"\nFetching NASDAQ data for {symbol}...")
    data = get_nasdaq_data(symbol)
    
    if data is None:
        print("Failed to fetch data. Please check your internet connection.")
        return
    
    movement_data = calculate_daily_movement(data)
    display_movement(movement_data)
    
    return movement_data


def track_multiple_days(symbol='^IXIC', days=5):
    """
    Track movement over multiple days.
    
    Args:
        symbol: Stock/index symbol
        days: Number of days to track
    """
    print(f"\nFetching NASDAQ data for last {days} days...")
    data = get_nasdaq_data(symbol, period=f'{days+1}d')
    
    if data is None or len(data) < 2:
        print("Failed to fetch data or insufficient data.")
        return
    
    print("\n" + "=" * 80)
    print("MULTI-DAY NASDAQ MOVEMENT TRACKER")
    print("=" * 80)
    
    for i in range(1, len(data)):
        prev_day = data.iloc[i-1]
        current_day = data.iloc[i]
        
        prev_close = prev_day['Close']
        current_close = current_day['Close']
        price_change = current_close - prev_close
        percent_change = (price_change / prev_close) * 100
        
        change_symbol = "▲" if price_change >= 0 else "▼"
        
        print(f"\n{current_day.name.date()}: {change_symbol} ${abs(price_change):,.2f} ({abs(percent_change):.2f}%)")
        print(f"  Close: ${current_close:,.2f} (Previous: ${prev_close:,.2f})")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    # Track today's movement
    track_nasdaq()
    
    # Uncomment to track multiple days
    # track_multiple_days(days=5)
