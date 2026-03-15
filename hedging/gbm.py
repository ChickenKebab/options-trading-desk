import numpy as np


def stock_price(s0, T, timestep, sigma, r):
    T = T/365
    timestep = timestep/365
    N = int(T/timestep)
    generated_stock_prices = np.zeros(N)
    generated_stock_prices[0] = s0
    Z = np.random.normal(0, 1, N)
    for i in range(N-1):
        generated_stock_prices[i+1] = generated_stock_prices[i]*np.exp((r-0.5*sigma**2)*timestep+sigma*np.sqrt(timestep)*Z[i])
    return generated_stock_prices






if __name__ == "__main__":
    generated_stock_prices = stock_price(100, 100, 1, 0.25, 0.05)
    print(generated_stock_prices)