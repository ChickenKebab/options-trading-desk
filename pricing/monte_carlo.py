import numpy as np

class MonteCarlo:

    def __init__(self, r, sigma, T, K, S, simulations, option_type):
        if option_type not in ['call', 'put']:
            raise ValueError("option_type must be 'call' or 'put'")

        self.r= r
        self.option_type = option_type
        self.sigma = sigma
        self.K = K
        self.T = T
        self.S = S
        self.simulations = simulations
        self.Z = self._simulate_Z()
        self.St_array = self._simulate_St()
        self.average_payoff = self._calculate_average_payoff()

    def _simulate_Z(self):
        Z = np.random.normal(0, 1, self.simulations)
        return Z
    
    def _simulate_St(self):
        St_array = self.S*np.exp((self.r-0.5*self.sigma**2)*self.T+self.sigma*np.sqrt(self.T)*self.Z)
        return St_array

    def _calculate_average_payoff(self):
        if self.option_type == 'call':
            payoff_array = np.maximum(self.St_array-self.K, 0)
            average_payoff = np.mean(payoff_array)
            return average_payoff
        else:
            payoff_array = np.maximum(self.K-self.St_array, 0)
            average_payoff = np.mean(payoff_array)
            return average_payoff
    
    def price(self):
        option_price = np.exp(-self.r*self.T)*self.average_payoff
        return option_price

    

if __name__ == "__main__":
    mc = MonteCarlo(S=150, K=150, r=0.05, sigma=0.25, T=1,
                    option_type='call', simulations=100000)
    print(f"Monte Carlo Call Price: ${mc.price():.4f}")
