type Listener = (...args: unknown[]) => void;

class EventEmitter {
  private events: Record<string, Listener[]> = {};

  on(event: string, listener: Listener) {
    if (!this.events[event]) {
      this.events[event] = [];
    }
    this.events[event].push(listener);
    return () => this.off(event, listener);
  }

  off(event: string, listener: Listener) {
    if (!this.events[event]) return;
    this.events[event] = this.events[event].filter((l) => l !== listener);
  }

  emit(event: string, ...args: unknown[]) {
    if (!this.events[event]) return;
    this.events[event].forEach((listener) => listener(...args));
  }
}

export const globalEvents = new EventEmitter();

export const EVENTS = {
  API_LOADING_START: "API_LOADING_START",
  API_LOADING_END: "API_LOADING_END",
};
