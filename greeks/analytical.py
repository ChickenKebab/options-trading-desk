from pricing.black_scholes import EuropeanOption
import numpy as np
from scipy.stats import norm

class EuropeanOptionsWithGreeks(EuropeanOption):

    def delta(self):
        if self.option_type == 'call':
            delta = norm.cdf(self.d1)
            return delta
        else:
            delta = norm.cdf(self.d1)-1
            return delta
    
    def gamma(self):
        gamma = norm.pdf(self.d1)/(self.S*self.sigma*np.sqrt(self.T))
        return gamma
    
    def vega(self):
        vega = self.S*np.sqrt(self.T)*norm.pdf(self.d1)
        return vega
    
    def theta(self):
        if self.option_type == 'call':
            theta = -(self.S*self.sigma*np.exp(-(self.d1**2)/2))/(2*np.sqrt(2*np.pi*self.T))-self.r*self.K*np.exp(-self.r*self.T)*(norm.cdf(self.d2))
            return theta
        else:
            theta = -(self.S*self.sigma*np.exp(-(self.d1**2)/2))/(2*np.sqrt(2*np.pi*self.T))+self.r*self.K*np.exp(-self.r*self.T)*(norm.cdf(-self.d2))
            return theta
    
    def rho(self):
        if self.option_type == 'call':
            rho = self.K*self.T*np.exp(-self.r*self.T)*(norm.cdf(self.d2))
            return rho
        else:
            rho = -self.K*self.T*np.exp(-self.r*self.T)*(norm.cdf(-self.d2))
            return rho


if __name__ == "__main__":
    option = EuropeanOptionsWithGreeks(S=150, K=150, r=0.05, sigma=0.25, T=1, option_type='call')
    print(f"d1:     {option.d1:.4f}")
    print(f"d2:     {option.d2:.4f}")
    print(f"N(d1):  {norm.cdf(option.d1):.4f}")
    print(f"N(d2):  {norm.cdf(option.d2):.4f}")
    print(f"pdf(d1):{norm.pdf(option.d1):.4f}")
    print(f"Price:  ${option.price():.4f}")
    print(f"Delta:  {option.delta():.4f}")
    print(f"Gamma:  {option.gamma():.4f}")
    print(f"Vega:   {option.vega():.4f}")
    print(f"Theta:  {option.theta():.4f}")
    print(f"Rho:    {option.rho():.4f}")