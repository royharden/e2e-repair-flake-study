"use strict";
// Always-present diagnostic hooks; never a genuine independent scoring oracle.
const seen = new Set();
for (const element of document.querySelectorAll("[data-oracle-id]")) {
  const id = element.getAttribute("data-oracle-id");
  if (!id || seen.has(id)) throw new Error("Duplicate/empty authored demo hook");
  seen.add(id);
}
