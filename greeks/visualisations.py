import numpy as np
import matplotlib.pyplot as plt
from greeks.analytical import EuropeanOptionsWithGreeks


def plot_greeks_vs_stock_price(K, r, sigma, T, option_type):
    stock_prices = np.linspace(50,250,200)
    deltas = []
    gammas = []
    vegas = []
    thetas = []
    rhos = []

    

    for i in stock_prices:
        option = EuropeanOptionsWithGreeks(S=i, K=K, r=r, sigma=sigma, T=T, option_type=option_type)
        deltas.append(option.delta())
        gammas.append(option.gamma())
        vegas.append(option.vega())
        thetas.append(option.theta())
        rhos.append(option.rho())

    
    fig, axes = plt.subplots(2, 3, figsize=(15,8))
    fig.suptitle(f'Greeks vs Stock Price | K={K}, sigma={sigma}, T={T}, {option_type}')

    axes[0,0].plot(stock_prices, deltas, color='blue')
    axes[0,0].set_title('Delta')

    axes[0,1].plot(stock_prices, gammas, color='orange')
    axes[0,1].set_title('Gamma')

    axes[0,2].plot(stock_prices, vegas, color='green')
    axes[0,2].set_title('Vega')

    axes[1,0].plot(stock_prices, thetas, color='red')
    axes[1,0].set_title('Theta')

    axes[1,1].plot(stock_prices, rhos, color='purple')
    axes[1,1].set_title('Rhos')

    axes[1,2].axis('off')

    for ax in axes.flat:
        ax.axvline(x=K, color='black', linestyle='--', alpha=0.3)
        ax.set_xlabel('Stock Price ($)')
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()



    
    


if __name__ == "__main__":
    plot_greeks_vs_stock_price(K=150, r=0.05, sigma=0.25, T=1, option_type='call')




