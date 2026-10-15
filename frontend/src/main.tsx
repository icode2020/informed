import React from "react";
import { createRoot } from "react-dom/client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

const queryClient = new QueryClient();

function App() {
  return (
    <main style={{ maxWidth: 720, margin: "4rem auto", padding: "0 1.5rem", fontFamily: "system-ui" }}>
      <h1>Informed</h1>
      <p>Understand how candidates align with your own priorities, using cited public evidence.</p>
      <p><strong>Foundation preview:</strong> voter profiles, authentication and matching are not yet enabled.</p>
      <p>We do not ask for or store your political preferences in this preview.</p>
    </main>
  );
}

createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>
  </React.StrictMode>
);
