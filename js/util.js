// Yield to the event loop without a timer.
// setTimeout is clamped to roughly once a second in a background tab, which would stall long searches
// (docking, screening) whenever the window is not in front. A MessageChannel round trip is a real task
// but is not subject to that clamp, so work keeps running at full speed in the background.
export function yieldToEventLoop() {
  return new Promise((resolve) => {
    const ch = new MessageChannel();
    ch.port1.onmessage = () => { ch.port1.close(); resolve(); };
    ch.port2.postMessage(0);
  });
}
