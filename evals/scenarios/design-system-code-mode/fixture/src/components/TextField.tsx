import "./TextField.css";

type Props = {
  label: string;
  value: string;
  onChange: (v: string) => void;
  error?: string; // validation message rendered inline under the field
  disabled?: boolean;
};

export function TextField({ label, value, onChange, error, disabled }: Props) {
  return (
    <label className={`field${error ? " field--error" : ""}`}>
      <span className="field__label">{label}</span>
      <input value={value} disabled={disabled} onChange={(e) => onChange(e.target.value)} />
      {error ? <span className="field__error" role="alert">{error}</span> : null}
    </label>
  );
}
