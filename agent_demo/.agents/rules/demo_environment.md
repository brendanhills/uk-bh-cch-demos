# Demo Environment & Hardware Guardrails

When designing, testing, and implementing features for this application, enforce the following presentation environment guardrails:

1. **Laptop Hardware Primary**:
   - Webcams are front-facing laptop cameras (`facingMode: "user"`). Never force mobile rear camera constraints (`facingMode: "environment"`) or mobile-only video dimensions.
   - Design camera overlays and document scanning guides for widescreen laptop feeds (e.g. centering a vertical portrait scanning guide inside the widescreen webcam preview).

2. **Live Presentation & Audience Clarity**:
   - Keep UI controls explicit, high-contrast, and easily visible during live screen-sharing and stage presentations.
   - Use clear visual indicators (such as green focus ready boxes and status banners) so an audience can follow the interaction effortlessly.

3. **Privacy & Presenter Control**:
   - Guarantee explicit camera controls (e.g., inline toggle, auto-stop on snapshot capture). Never run stealth or pre-warmed background video streams that keep camera activity lights on unexpectedly.

4. **Low-Friction Presenter UX**:
   - Minimize click steps for the presenter (e.g., single-tap camera snapshot with privacy auto-off). Avoid unnecessary modal popups or confirmation dialogs that interrupt presentation flow.
