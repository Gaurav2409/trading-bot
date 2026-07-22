interface Props {
  accountId: string;
  killMode: string;
  onEntryDisable: (accountId: string) => void;
}

// Kill-state controls. Entry-disable / reduce-only / halt are the only mutating
// actions; there is no order-entry control and no family/FX execution control.
export function RiskControls({ accountId, killMode, onEntryDisable }: Props) {
  return (
    <section aria-label="Risk controls">
      <h2>Controls — {accountId}</h2>
      <p>Kill state: <span data-testid={`kill-${accountId}`}>{killMode}</span></p>
      <button type="button" onClick={() => onEntryDisable(accountId)}>
        Disable new entries
      </button>
    </section>
  );
}
