/* Session tokens stay in memory, including in local development. */
export class ApiError extends Error {
  constructor(message, status = 0, fields = null) { super(message); this.status = status; this.fields = fields; }
}
function errorText(value) {
  if (typeof value === "string") return value;
  if (Array.isArray(value)) return value.map(errorText).join(" · ");
  if (value && typeof value === "object" && "detail" in value) return errorText(value.detail);
  return Object.entries(value || {}).map(([key, item]) => key === "detail" ? errorText(item) : `${key}: ${errorText(item)}`).join("\n");
}
export class Api {
  #access = "";
  #refresh = "";
  #refreshing = null;
  #epoch = 0;
  setSession(data) { this.#epoch++; this.#access = data.access; this.#refresh = data.refresh; }
  clear() { this.#epoch++; this.#access = ""; this.#refresh = ""; }
  get authenticated() { return Boolean(this.#access); }
  async request(path, {method = "GET", data, signal, blob = false, retry = true, anonymous = false} = {}) {
    const url = new URL(path.startsWith("/api/") ? path : `/api/v1/${path}`, location.origin);
    if (url.origin !== location.origin || !url.pathname.startsWith("/api/v1/")) throw new ApiError("Invalid API URL");
    const token = anonymous ? "" : this.#access;
    const epoch = this.#epoch;
    const headers = {Accept: blob ? "*/*" : "application/json"};
    if (token) headers.Authorization = `Bearer ${token}`;
    const csrf = document.querySelector('[name="csrfmiddlewaretoken"]')?.value;
    if (csrf) headers["X-CSRFToken"] = csrf;
    if (data !== undefined && !(data instanceof FormData)) headers["Content-Type"] = "application/json";
    const controller = new AbortController();
    const abort = () => controller.abort();
    if (signal?.aborted) controller.abort();
    signal?.addEventListener("abort", abort, {once: true});
    const timeout = setTimeout(abort, 30000);
    let response, raw, bodyBlob;
    try {
      response = await fetch(url, {method, headers, body: data instanceof FormData ? data : data === undefined ? undefined : JSON.stringify(data), credentials: "same-origin", cache: "no-store", signal: controller.signal});
      if (response.ok && blob) bodyBlob = await response.blob();
      else raw = await response.text();
    } catch (error) {
      if (signal?.aborted) throw error;
      throw new ApiError("network", 0);
    } finally { clearTimeout(timeout); signal?.removeEventListener("abort", abort); }
    if (token && epoch !== this.#epoch) throw new ApiError("sessionChanged", 401);
    if (response.status === 401 && token && retry && this.#refresh) {
      // Late failures may belong to the previous access token. Concurrent requests
      // share one renewal, so rotating refresh tokens cannot invalidate each other.
      if (token === this.#access) await this.#renew();
      return this.request(path, {method, data, signal, blob, anonymous, retry: false});
    }
    if (response.ok && blob) return bodyBlob;
    // Proxies and failed backends may return HTML instead of JSON. Preserve
    // the service failure status without showing a parser error to customers.
    if (response.status >= 500) throw new ApiError("serviceUnavailable", response.status);
    let body = null;
    if (raw) {
      try { body = JSON.parse(raw); }
      catch { throw new ApiError("invalidResponse", response.status); }
    }
    if (!response.ok) throw new ApiError(errorText(body) || `HTTP ${response.status}`, response.status, body);
    if (!raw && response.status !== 204 && !url.pathname.endsWith("/service-center/")) throw new ApiError("invalidResponse", response.status);
    return body;
  }
  async #renew() {
    const epoch = this.#epoch;
    if (this.#refreshing?.epoch !== epoch) {
      const pending = {epoch, promise: null};
      pending.promise = this.request("auth/refresh/", {method: "POST", data: {refresh: this.#refresh}, retry: false, anonymous: true})
        .then(data => {
          if (epoch !== this.#epoch) throw new ApiError("sessionChanged", 401);
          this.#access = data.access;
          if (data.refresh) this.#refresh = data.refresh;
        })
        .catch(error => { if (epoch === this.#epoch) this.clear(); throw error; })
        .finally(() => { if (this.#refreshing === pending) this.#refreshing = null; });
      this.#refreshing = pending;
    }
    return this.#refreshing.promise;
  }
  async all(path, {signal, anonymous = false} = {}) {
    const results = [];
    let next = path;
    for (let page = 0; next && page < 100; page++) {
      const data = await this.request(next, {signal, anonymous});
      if (Array.isArray(data)) return results.concat(data);
      if (!data || !Array.isArray(data.results) || (data.next != null && typeof data.next !== "string")) throw new ApiError("invalidResponse", 200);
      results.push(...data.results);
      next = data.next ? new URL(data.next, location.origin).pathname + new URL(data.next, location.origin).search : null;
    }
    if (next) throw new ApiError("catalogLimit");
    return results;
  }
  async logout() {
    const epoch = this.#epoch;
    try { if (this.#refresh) await this.request("auth/logout/", {method: "POST", data: {refresh: this.#refresh}}); }
    finally { if (epoch === this.#epoch) this.clear(); }
  }
}
