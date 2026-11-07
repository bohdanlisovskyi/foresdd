import { createRoot } from "react-dom/client";
import "./styles/tokens.css";
import { InvoicesPage } from "./pages/InvoicesPage";

createRoot(document.getElementById("root")!).render(<InvoicesPage invoices={[]} />);
