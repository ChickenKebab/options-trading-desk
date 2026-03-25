import streamlit as st
from pricing.black_scholes import EuropeanOption
from pricing.monte_carlo import MonteCarlo
from greeks.analytical import EuropeanOptionsWithGreeks
from greeks.visualisations import plot_greeks_vs_stock_price
from hedging.gbm import stock_price
from hedging.simulator import HedingSimulatorEngine
from volatility.smile import VolatilitySurface


st.set_page_config(page_title="Options Trading Desk", layout="wide")
st.title("Options Trading Desk")

# shared inputs in sidebar
st.sidebar.header("Parameters")
S = st.sidebar.number_input("Stock Price ($)", value=150.0, min_value=0.1)
K = st.sidebar.number_input("Strike Price ($)", value=150.0)
r = st.sidebar.number_input("Risk Free Rate", value=0.05, min_value=0.01, max_value=0.20)
T_days = st.sidebar.number_input("Days to Expiry", value=90, min_value=1, max_value=1000)
T = T_days / 365
sigma = st.sidebar.slider("Volatility", min_value=0.01, max_value=1.0, value=0.25)
option_type = st.sidebar.selectbox("Option Type", ["call", "put"])
simulations = st.sidebar.slider("MC Simulations", min_value=1000, max_value=1000000, value=100000)



tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Options Pricer",
    "Greeks",
    "Hedge Simulator",
    "Volatility Smile",
    "Volatility Surface"
])

with tab1:
    if st.button("Calculate"):
        option = EuropeanOptionsWithGreeks(S=S, K=K, r=r, sigma=sigma, T=T, option_type=option_type)
        mc = MonteCarlo(S=S, K=K, r=r, sigma=sigma, T=T, simulations=simulations, option_type=option_type)

        st.subheader("Prices")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Black-Scholes Price", f"${option.price():.4f}")
        with col2:
            st.metric("Monte Carlo Price", f"${mc.price():.4f}")

        st.subheader("Greeks")
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Delta", f"{option.delta():.4f}")
        with col2:
            st.metric("Gamma", f"{option.gamma():.4f}")
        with col3:
            st.metric("Vega", f"{option.vega():.4f}")
        with col4:
            st.metric("Theta", f"{option.theta():.4f}")
        with col5:
            st.metric("Rho", f"{option.rho():.4f}")

with tab2:
    if st.button("Plot Greeks"):
        fig = plot_greeks_vs_stock_price(K, r, sigma, T, option_type)
        st.pyplot(fig)

with tab3:
    n_options = st.number_input("Amount of Options", min_value=1, max_value=1000, value=100)
    rebalancing_frequency = st.number_input("Rebalancing Frequency (How often do you want the delta to be neutralised in days)", value=1, min_value=1, max_value=30)


    if st.button("Run Simulation"):
        daily_path = stock_price(S, T_days, rebalancing_frequency, sigma, r)
        engine = HedingSimulatorEngine(r, rebalancing_frequency, K, T, sigma, option_type, n_options)
        engine.run(daily_path)

        final_stock_price = daily_path[-1]
        if option_type == "call":
            option_payoff = max(final_stock_price - K, 0) * n_options
        else:
            option_payoff = max(K - final_stock_price, 0) * n_options
        final_portfolio = engine.portfolio_values[-1]
        hedging_error = final_portfolio - option_payoff


        

        st.subheader("Simulation Results")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Initial Stock Price", f"${daily_path[0]:.2f}")
        with col2:
            st.metric("Final Stock Price", f"{final_stock_price:.2f}")
        with col3:
            st.metric("Option Payoff", f"{option_payoff:.2f}")
        with col4:
            st.metric("Final Portfolio Value", f"{final_portfolio:.2f}")
        
        st.metric("Hedging Error", f"${hedging_error:.2f}")

        fig = engine.results(daily_path)
        st.pyplot(fig)



with tab4:
    ticker = st.text_input("Ticker", value="AAPL")
    
    if st.button("Load Volatility Smile"):
        with st.spinner("Downloading options data..."):
            vs = VolatilitySurface(ticker=ticker, r=r)
            vs.calculate_iv_surface_2()
        
        expiries = vs.df['expiration'].unique()
        selected_expiry = st.selectbox("Select Expiry", expiries)
        
        fig = vs.plot_smile(selected_expiry)
        st.pyplot(fig)

with tab5:
    ticker_surface = st.text_input("Ticker", value="AAPL", key="t5_ticker")
    
    if st.button("Load Volatility Surface"):
        with st.spinner("Downloading options data..."):
            vs_surface = VolatilitySurface(ticker=ticker_surface, r=r)
            vs_surface.calculate_iv_surface_2()
        
        fig = vs_surface.plot_surface()
        st.pyplot(fig)


