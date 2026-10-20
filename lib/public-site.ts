// Only the confirmed marketing domains expose a public root. Other hosts keep the protected dashboard.
export const PUBLIC_SALES_HOSTS = new Set(["urakkaluotsi.fi", "www.urakkaluotsi.fi"]);
export function salesEntryPath(host: string | null, pathname: string): string | null {
  const hostname = host?.toLowerCase().replace(/:\d+$/, "");
  return pathname === "/" && hostname && PUBLIC_SALES_HOSTS.has(hostname) ? "/esittely" : null;
}
export function confirmedPublicOrigin(value: string | undefined): string | undefined {
  return value === "https://urakkaluotsi.fi" ? value : undefined;
}
