/**
 * Utility functions for robust date parsing and comparisons across different formats
 * (ISO YYYY-MM-DD, human '12 Nov 2025', slash '12/11/2025', etc.)
 */

const dateCache = new Map<string, Date | null>();

export function parseFlexibleDate(dateStr?: string | null): Date | null {
  if (!dateStr || typeof dateStr !== 'string') return null;
  const s = dateStr.trim();
  if (!s || ['-', 'completed', 'n/a', 'no data', 'not set', 'tbd', 'none', 'unknown', 'null', 'undefined'].includes(s.toLowerCase())) {
    return null;
  }

  if (dateCache.has(s)) {
    return dateCache.get(s) ?? null;
  }

  const computeDate = (): Date | null => {
    // Direct JS Date parse (handles '12 Nov 2025', '2026-07-05', etc.)
    let d = new Date(s);
    if (!isNaN(d.getTime())) return d;

    // Replace dashes with spaces (e.g. 12-Nov-2025 -> 12 Nov 2025)
    const cleaned = s.replace(/-/g, ' ');
    d = new Date(cleaned);
    if (!isNaN(d.getTime())) return d;

    // Split by slashes or dots (e.g. 12/11/2026 or 2026.07.05)
    const parts = s.split(/[/.]/);
    if (parts.length === 3) {
      const p1 = parseInt(parts[0], 10);
      const p2 = parseInt(parts[1], 10);
      const p3 = parseInt(parts[2], 10);

      if (!isNaN(p1) && !isNaN(p2) && !isNaN(p3)) {
        if (p1 > 1000) {
          d = new Date(p1, p2 - 1, p3);
        } else if (p3 > 1000) {
          const fullYear = p3 < 100 ? 2000 + p3 : p3;
          // Assume DD/MM/YYYY
          d = new Date(fullYear, p2 - 1, p1);
        }
        if (!isNaN(d.getTime())) return d;
      }
    }

    return null;
  };

  const result = computeDate();
  dateCache.set(s, result);
  return result;
}

export function formatDateShort(date: Date): string {
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  const m = months[date.getMonth()];
  const d = String(date.getDate()).padStart(2, '0');
  return `${m} ${d}`;
}
