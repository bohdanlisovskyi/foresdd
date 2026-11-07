import { useState } from "react";
import { Button } from "../components/Button";
import { Card } from "../components/Card";
import { TextField } from "../components/TextField";

// Desktop dashboard screen: a filter field + the invoice list, composed from the shared primitives.
export function InvoicesPage({ invoices }: { invoices: { id: string; total: string }[] }) {
  const [query, setQuery] = useState("");
  return (
    <Card title="Invoices">
      <TextField label="Search" value={query} onChange={setQuery} />
      {invoices.length === 0 ? (
        <p style={{ color: "var(--color-muted)" }}>No invoices yet — create your first one.</p>
      ) : (
        <ul>
          {invoices.map((i) => (
            <li key={i.id}>{i.id} — {i.total}</li>
          ))}
        </ul>
      )}
      <Button>New invoice</Button>
    </Card>
  );
}
