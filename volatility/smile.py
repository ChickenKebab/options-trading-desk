'''
smile.py

Downloads real options data and calculates implied volatility across 
all strikes and expiries.

The purpose of this is to showcase that black-scholes is wrong in assumptions but correct in framework. 
Similar to Newton's Laws of motion.
'''
import numpy as np
from openbb import obb
from greeks.analytical import EuropeanOptionsWithGreeks
from datetime import date
import matplotlib.pyplot as plt


class VolatilitySurface:

    def __init__(self, ticker, r):
        self.ticker = ticker
        self.r = r
        result = obb.derivatives.options.chains(symbol=ticker)
        self.df = result.to_df()
        self.S = self.df['underlying_price'].iloc[0]
        self.initial_guess = 0.2

    def implied_volatility_solver(self, market_price, K, T, option_type):
        sigma = self.initial_guess

        for i in range(100):
            option = EuropeanOptionsWithGreeks(self.S, K, self.r, sigma, T, option_type)
            bs_price = option.price()
            vega = option.vega()

            diff = bs_price - market_price

            if abs(diff) < 1e-6:
                return sigma

            if vega == 0:
                return None

            sigma = sigma - diff/vega
            sigma = max(0.001, min(sigma, 10.0))

            if sigma <= 0:
                return None

        return None

    def calculate_iv_surface(self):
        ivs = []

        for _, row in self.df.iterrows():
            if row['bid'] <= 0 or row['ask'] <= 0:
                ivs.append(None)
                continue

            market_price = (row['bid'] + row['ask']) / 2
            if market_price < 0.05:
                ivs.append(None)
                continue

            T = (row['expiration'] - date.today()).days / 365
            if T <= 0:
                ivs.append(None)
                continue

            if market_price <= 0:
                ivs.append(None)
                continue

            iv = self.implied_volatility_solver(
                market_price=market_price,
                K=row['strike'],
                T=T,
                option_type=row['option_type']
            )

            ivs.append(iv)

        self.df['calculated_iv'] = ivs

    def calculate_iv_surface_2(self):
        self.df['calculated_iv'] = self.df['implied_volatility']

    def plot_smile(self, expiry):
        # use puts for strikes below current price
        # use calls for strikes above current price
        puts_mask = (
            (self.df['expiration'] == expiry) &
            (self.df['option_type'] == 'put') &
            (self.df['strike'] >= self.S * 0.7) &
            (self.df['strike'] <= self.S) &
            (self.df['calculated_iv'] > 0.01) &
            (self.df['calculated_iv'] < 2.0)
        )
        calls_mask = (
            (self.df['expiration'] == expiry) &
            (self.df['option_type'] == 'call') &
            (self.df['strike'] >= self.S) &
            (self.df['strike'] <= self.S * 1.5) &
            (self.df['calculated_iv'] > 0.01) &
            (self.df['calculated_iv'] < 2.0)
        )
        
        puts_data = self.df[puts_mask].dropna(subset=['calculated_iv'])
        calls_data = self.df[calls_mask].dropna(subset=['calculated_iv'])
        
        # combine
        import pandas as pd
        data = pd.concat([puts_data, calls_data]).sort_values('strike')
        
        if len(data) == 0:
            print(f"No valid data for expiry {expiry}")
            return
        
        plt.figure(figsize=(10, 6))
        plt.plot(data['strike'], data['calculated_iv'] * 100, marker='o')
        plt.axvline(x=self.S, color='black', linestyle='--', alpha=0.5, label=f'Current Price ${self.S:.2f}')
        plt.xlabel('Strike Price ($)')
        plt.ylabel('Implied Volatility (%)')
        plt.title(f'Volatility Smile — AAPL {expiry}')
        plt.legend()
        plt.grid(True, alpha=0.3)
        return plt.gcf()

    def plot_surface(self):
        calls = self.df[
            (self.df['option_type'] == 'call') &
            (self.df['strike'] >= self.S * 0.7) &
            (self.df['strike'] <= self.S * 1.5) &
            (self.df['calculated_iv'] > 0.01) &
            (self.df['calculated_iv'] < 2.0)
        ].dropna(subset=['calculated_iv'])

        today = date.today()
        calls = calls.copy()
        calls['dte'] = calls['expiration'].apply(lambda x: (x - today).days)

        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111, projection='3d')

        ax.scatter(
            calls['strike'],
            calls['dte'],
            calls['calculated_iv'] * 100,
            c=calls['calculated_iv'] * 100,
            cmap='viridis',
            alpha=0.6
        )

        ax.set_xlabel('Strike ($)')
        ax.set_ylabel('Days to Expiry')
        ax.set_zlabel('Implied Volatility (%)')
        ax.set_title('AAPL Volatility Surface')
        return fig


if __name__ == "__main__":
    vs = VolatilitySurface(ticker="AAPL", r=0.05)

    vs.calculate_iv_surface_2()

    print(vs.df.groupby('expiration')['implied_volatility'].count())

    # try a few expiries manually
    for exp in [date(2026, 6, 18), date(2026, 9, 18), date(2026, 12, 18)]:
        print(f"\nPlotting smile for {exp}")
        vs.plot_smile(exp)

    vs.plot_surface()