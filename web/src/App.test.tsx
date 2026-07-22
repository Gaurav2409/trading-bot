import { describe, expect, it } from "vitest";
import { fireEvent, render, screen } from "@testing-library/react";
import { App } from "./App";

describe("Operator console", () => {
  it("shows Zerodha and Alpaca as separate partitions", () => {
    render(<App />);
    expect(screen.getByTestId("account-kite-1").getAttribute("data-broker")).toBe("kite");
    expect(screen.getByTestId("account-alpaca-1").getAttribute("data-broker")).toBe("alpaca");
  });

  it("surfaces an external/manual holding that affects the portfolio", () => {
    render(<App />);
    expect(screen.getByTestId("external-TESTCO")).toHaveTextContent("manual_matched_broker");
  });

  it("explains why a candidate is blocked", () => {
    render(<App />);
    const blocked = screen.getByTestId("candidate-ILLIQ");
    expect(blocked).toHaveTextContent("circuit_locked");
    expect(blocked).toHaveTextContent("insufficient_liquidity");
  });

  it("disables entries for one broker without touching the other", () => {
    render(<App />);
    const [disableKite] = screen.getAllByText("Disable new entries");
    fireEvent.click(disableKite);
    expect(screen.getByTestId("kill-kite-1")).toHaveTextContent("entry_disabled");
    expect(screen.getByTestId("kill-alpaca-1")).toHaveTextContent("active");
  });

  it("exposes no family or FX execution control", () => {
    render(<App />);
    expect(screen.queryByText(/family/i)).toBeNull();
    expect(screen.queryByText(/FX|forex/i)).toBeNull();
  });
});
