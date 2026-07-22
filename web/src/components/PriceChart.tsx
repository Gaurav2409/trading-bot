import { useEffect, useRef } from "react";
import { createChart, type UTCTimestamp } from "lightweight-charts";

export interface OsBar {
  time: UTCTimestamp;
  open: number;
  high: number;
  low: number;
  close: number;
}

// TradingView Lightweight Charts fed ONLY by the OS's validated bars. Agents do
// not consume this chart; it is human inspection only, and it never fetches
// hidden third-party chart data.
export function PriceChart({ bars }: { bars: OsBar[] }) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current) return;
    const chart = createChart(containerRef.current, { height: 240 });
    const series = chart.addCandlestickSeries();
    series.setData(bars);
    return () => chart.remove();
  }, [bars]);

  return <div aria-label="Price chart" data-testid="price-chart" ref={containerRef} />;
}
