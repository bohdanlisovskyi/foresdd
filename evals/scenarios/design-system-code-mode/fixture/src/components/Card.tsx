type Props = { title?: string; children: React.ReactNode };

export function Card({ title, children }: Props) {
  return (
    <section
      style={{
        background: "var(--color-surface)",
        padding: "var(--space-6)",
        borderRadius: "var(--radius-md)",
      }}
    >
      {title ? <h2 style={{ fontSize: "var(--font-size-lg)" }}>{title}</h2> : null}
      {children}
    </section>
  );
}
