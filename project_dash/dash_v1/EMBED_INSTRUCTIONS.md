# Embedding the Corporate Risk & Issue Dashboard in Google Sites

This guide explains how to embed your dynamic **Corporate Risk & Issue Register Dashboard** into your internal Google Site (`https://sites.google.com/corp/google.com/disp/home`).

Because you are working on a corporate Google Site, there are two easy, robust methods to embed the dashboard. 

---

## Method 1: Embed by URL (Recommended & Easiest)

Google Sites has a native "Embed" tool that accepts direct URLs. It automatically configures the sandbox and responsive sizing.

1. Open your Google Site editor at `https://sites.google.com/corp/google.com/disp/home`.
2. On the right-hand panel, select **Insert** > **Embed**.
3. Under the **By URL** tab, paste the following **Shared App URL**:
   ```
   https://ais-pre-zwxmb3amixfih2ibnlgrsr-95296462601.asia-east1.run.app
   ```
4. Google Sites will show a preview of the dashboard. Click **Insert**.
5. Drag the borders of the embedded window in the editor to make it wider and taller (we recommend at least **1200px wide** and **800px tall** for comfortable viewing of the matrices and ledgers).

---

## Method 2: Embed via Custom HTML Code Block

If you want absolute control over the iframe constraints, scrolling style, and security sandboxing, you can paste custom HTML code directly.

1. Open your Google Site editor.
2. Select **Insert** > **Embed**.
3. Switch to the **Embed code** tab.
4. Paste the following highly optimized, full-screen responsive iframe snippet:

```html
<div style="width: 100%; height: 100vh; min-height: 800px; border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03); background-color: #f8fafc;">
  <iframe 
    src="https://ais-pre-zwxmb3amixfih2ibnlgrsr-95296462601.asia-east1.run.app" 
    style="width: 100%; height: 100%; border: none;" 
    allow="clipboard-read; clipboard-write; fullscreen"
    sandbox="allow-storage-access-by-user-activation allow-scripts allow-same-origin allow-popups allow-popups-to-escape-sandbox allow-forms"
    title="Corporate Risk & Issue Registry"
  ></iframe>
</div>
```

5. Click **Next** and then **Insert**.
6. Resize the custom widget block to occupy the desired grid space on your webpage.

---

## Technical & Security Considerations for Corp-Net Users

As a Google corp-net user working at `sites.google.com/corp/google.com/...`:

1. **Access Authorization**: The Shared App URL (`https://ais-pre-...`) is hosted securely on Cloud Run. Any corp user who visits your Google Site will be able to view and interact with the dashboard directly inside the embed, provided their browser has standard web access (no special corp VPN configurations required, as it is a public URL).
2. **LocalStorage Persistence**: The application saves database edits (adding, updating, or deleting risks or issues) directly to the browser's **LocalStorage**. If multiple users need to collaborate on a single, shared database, or if you want data to persist permanently across multiple devices without depending on browser cache, we can easily set up **Firebase Firestore** to securely sync edits to a cloud database!
3. **If You Encounter a "Page Not Found" Error**:
   * **Exact URL**: Ensure that you are pasting the clean, exact URL without any extra trailing symbols, parameters, or relative subpaths (e.g., do not append `/WholeDataTab` or `/overview`).
   * **Iframe Sandbox Constraints**: In some corporate-managed environments, Google Sites enforces rigid iframe sandboxing. If you embed via Method 2, the `sandbox` attributes included in the code block (`allow-scripts allow-same-origin allow-popups allow-popups-to-escape-sandbox`) will bypass these restrictions and ensure all interactive elements, modal overlays, drag-to-scroll features, and pop-out window actions run seamlessly.
