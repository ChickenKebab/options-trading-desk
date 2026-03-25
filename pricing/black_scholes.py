'''
black_scholes.py

Provides the tools for pricing a European Option using Black Scholes. 

It takes in the current stock price, strike price, risk free rate, volatility and time until expiry.
Calculates d1,d2 and the option price.
'''
import numpy as np
from scipy.stats import norm


class EuropeanOption:

    def __init__(self, S, K, r, sigma, T, option_type):
        if option_type not in ['call', 'put']:
            raise ValueError("option_type must be 'call' or 'put'")  
        self.S = S
        self.K = K
        self.r = r
        self.sigma = sigma
        self.T = T
        self.option_type = option_type.lower() 
        self.d1 = self._d1()
        self.d2 = self._d2()

    
    def _d1(self):
        d1 = (np.log(self.S/self.K) + (self.r + 0.5*self.sigma**2)*self.T)/(self.sigma*np.sqrt(self.T))
        return d1
    

    def _d2(self):
        d2 = self.d1 - self.sigma*np.sqrt(self.T)
        return d2
    
    def price(self):
        
        if self.option_type == 'call':
            call_price = self.S*(norm.cdf(self.d1))-self.K*np.exp(-self.r*self.T)*(norm.cdf(self.d2))
            return call_price
        
        else:
            put_price = self.K*np.exp(-self.r*self.T)*(norm.cdf(-self.d2))-self.S*(norm.cdf(-self.d1))
            return put_price
        



#if __name__ == "__main__":
   # call = EuropeanOption(S=150, K=150, r=0.05, sigma=0.25, T=1, option_type='call')
   # print(f"d1: {call.d1:.4f}")
   # print(f"d2: {call.d2:.4f}")
  #  print(f"Call Price: ${call.price():.4f}")
    
   # put = EuropeanOption(S=150, K=150, r=0.05, sigma=0.25, T=1, option_type='put')
   # print(f"Put Price: $ {put.price():.4f}")