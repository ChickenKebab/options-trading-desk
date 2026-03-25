'''
simulator.py

Simulates delta hedging a European option position over time.

Sells N options at t=0, builds a replicating portfolio using the Black-Scholes 
delta, and rebalances at a fixed interval until expiry. Tracks portfolio value, 
cash, shares and delta at every step.
'''
import numpy as np
from greeks.analytical import EuropeanOptionsWithGreeks
from hedging.gbm import stock_price
import matplotlib.pyplot as plt


class HedingSimulatorEngine:

    def __init__(self, r, rebalancing_timestep, K, T, sigma, option_type, N_options):
        if option_type not in ['call', 'put']:
            raise ValueError("option_type must be 'call' or 'put'")  
        self.option_type = option_type
        self.rebalancing_timestep = rebalancing_timestep
        self.K = K
        self.T = T
        self.r = r
        self.sigma = sigma
        self.N_options = N_options


        self.cash = 0
        self.shares = 0
        self.delta = 0

        self.portfolio_values = []
        self.delta_history = []
        self.share_history = []
        self.cash_history = []
    

    def initialise(self, S):
        option = EuropeanOptionsWithGreeks(S, self.K, self.r, self.sigma, self.T, self.option_type)
        delta = option.delta()
        option_price = option.price()
        amount_of_shares_needed = delta*self.N_options
        price = amount_of_shares_needed*S
        self.cash = -(price-(option_price*self.N_options))
        self.shares = amount_of_shares_needed
        self.delta = delta
        self.portfolio_values.append(self.shares * S + self.cash)
        self.delta_history.append(self.delta)
        self.share_history.append(self.shares)
        self.cash_history.append(self.cash)
    

    def rebalance(self, S_current, T_remaining):
        self.cash *= np.exp(self.r * self.rebalancing_timestep/365)
        option = EuropeanOptionsWithGreeks(S_current, self.K, self.r, self.sigma, T_remaining, self.option_type)
        delta = option.delta()

        shares_needed = (delta*self.N_options)-self.shares
        self.shares += shares_needed
        self.cash -= shares_needed*S_current
        self.delta = delta

        self.portfolio_values.append(self.shares * S_current + self.cash)
        self.delta_history.append(self.delta)
        self.share_history.append(self.shares)
        self.cash_history.append(self.cash)

    
    def run(self, stock_generated):



        self.initialise(stock_generated[0])
        
        for i in range(len(stock_generated)-1):
            T_remaining = max(self.T-(i*self.rebalancing_timestep/365), 1e-6)
            self.rebalance(stock_generated[i+1], T_remaining)
            print(f'Current Shares: {self.shares}, \nCurrent Cash: {self.cash}')
            
    
    def results(self, stock_generated):
        
        if self.option_type == 'call':
            option_payoff = max(stock_generated[-1]-self.K,0) * self.N_options
        else:
            option_payoff = max(self.K - stock_generated[-1], 0) * self.N_options
        
        hedging_error = self.portfolio_values[-1] - option_payoff



        print("-"*40)
        print("Simulation Results")
        print("-"*45)
        print(f"Initial Stock Price: {stock_generated[0]}")
        print(f"Final Stock Price: {stock_generated[-1]}")
        print(f"Option Payoff: {option_payoff}")
        print(f"Final Replicating Portfolio Value: {self.portfolio_values[-1]}")
        print(f"Hedging error: ${hedging_error}")


        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

        ax1.plot(stock_generated, color='blue')
        ax1.axhline(y=self.K, color='black', linestyle='--', alpha=0.3, label='Strike')
        ax1.set_title('Stock Price Path')
        ax1.set_xlabel('Time Step')
        ax1.set_ylabel('Stock Price ($)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        ax2.plot(self.portfolio_values, color='green', label='Hedge Portfolio')
        ax2.set_title('Portfolio Value Over Time')
        ax2.set_xlabel('Time Step')
        ax2.set_ylabel('Value ($)')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        return fig





