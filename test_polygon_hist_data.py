import os
from dotenv import load_dotenv
from polygon import RESTClient
from datetime import datetime

load_dotenv('.env')
api_key = os.getenv('POLYGON_API_KEY')

client = RESTClient(api_key)

print('Testing historical options OHLC data...')
print()

# Get a recent SPY call option
contracts = client.list_options_contracts(
    underlying_ticker='SPY',
    limit=1
)

contract = next(iter(contracts))
ticker = contract.ticker

print(f'Testing contract: {ticker}')
print(f'Strike: ${contract.strike_price}')
print(f'Expiration: {contract.expiration_date}')
print()

# Try to get historical data for last 5 days
try:
    bars = client.get_aggs(
        ticker=ticker,
        multiplier=1,
        timespan='day',
        from_='2024-10-21',
        to='2024-10-25',
        limit=10
    )

    bar_list = list(bars)

    if len(bar_list) > 0:
        print(f'[SUCCESS] Retrieved {len(bar_list)} historical price bars!')
        print()
        print('Sample data:')
        for bar in bar_list[:3]:
            dt = datetime.fromtimestamp(bar.timestamp / 1000)
            print(f'  {dt.date()}: Open=${bar.open:.2f} Close=${bar.close:.2f} Volume={bar.volume}')
        print()
        print('*** YOUR POLYGON PLAN HAS HISTORICAL OPTIONS DATA! ***')
    else:
        print('[WARN] No historical bars found for this contract')
        print('Contract might be too new or illiquid')

except Exception as e:
    print(f'[ERROR] {type(e).__name__}: {e}')
