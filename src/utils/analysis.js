// Technical Analysis Utilities

export const calculateRSI = (prices, period = 14) => {
  const changes = prices.slice(1).map((price, i) => price - prices[i]);
  const gains = changes.map(change => Math.max(change, 0));
  const losses = changes.map(change => Math.abs(Math.min(change, 0)));
  
  const avgGain = gains.slice(0, period).reduce((sum, gain) => sum + gain, 0) / period;
  const avgLoss = losses.slice(0, period).reduce((sum, loss) => sum + loss, 0) / period;
  
  const rs = avgGain / avgLoss;
  return 100 - (100 / (1 + rs));
};

export const calculateMACD = (prices, fastPeriod = 12, slowPeriod = 26, signalPeriod = 9) => {
  // MACD calculation logic
  return {
    macd: 0,
    signal: 0,
    histogram: 0
  };
};

export const calculateEMA = (prices, period) => {
  const multiplier = 2 / (period + 1);
  let ema = prices[0];
  
  return prices.slice(1).map(price => {
    ema = (price - ema) * multiplier + ema;
    return ema;
  });
};