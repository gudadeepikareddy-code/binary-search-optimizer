const META = {
  capacity: {
    values: "Package weights (in delivery order)", param: "Days allowed",
    help: "Packages must ship in order. Find the smallest daily capacity that finishes within the allowed days.",
    example: ["1,2,3,4,5,6,7,8,9,10", 5],
  },
  speed: {
    values: "Task sizes (e.g. pile sizes)", param: "Hours allowed",
    help: "Each hour you work on one task at your speed. Find the slowest speed that finishes in time.",
    example: ["3,6,7,11", 8],
  },
  spacing: {
    values: "Stop positions (distinct)", param: "Number of stops to pick",
    help: "Choose K positions so the closest pair is as far apart as possible.",
    example: ["1,2,4,8,9", 3],
  },
};
const $ = (id) => document.getElementById(id);

function refreshLabels() {
  const m = META[$("problem").value];
  $("valuesLabel").textContent = m.values;
  $("paramLabel").textContent = m.param;
  $("help").textContent = m.help;
}

function row(cells) {
  const tr = document.createElement("tr");
  cells.forEach((c) => {
    const td = document.createElement("td");
    if (c && typeof c === "object") { td.textContent = c.text; td.className = c.cls; }
    else td.textContent = c;
    tr.appendChild(td);
  });
  return tr;
}

function bar(label, value, max, cls) {
  const d = document.createElement("div");
  d.className = "bar";
  const b = document.createElement("b"); b.textContent = label;
  const i = document.createElement("i"); i.className = cls;
  i.style.width = Math.max(1, (value / max) * 70) + "%";
  const s = document.createElement("span"); s.textContent = value;
  d.append(b, i, s);
  return d;
}

function showResult(r) {
  $("resultCard").hidden = false;
  $("answerLabel").textContent = r.label + ":";
  $("answer").textContent = r.answer;
  $("detail").textContent =
    "Search range " + r.search_range[0] + " to " + r.search_range[1] + ". " +
    Object.entries(r.details).map(([k, v]) => k.replace(/_/g, " ") + " = " + v).join(", ") + ".";

  const bs = r.binary_search, bl = r.baseline;
  $("bsChecks").textContent = bs.checks;
  $("bsTime").textContent = bs.time_ms;
  $("bars").replaceChildren();
  if (bl.skipped) {
    $("linChecks").textContent = $("linTime").textContent = "skipped";
    $("match").textContent = bl.reason;
  } else {
    $("linChecks").textContent = bl.checks;
    $("linTime").textContent = bl.time_ms;
    $("match").textContent = bl.matches ? "Yes, both agree" : "No, mismatch!";
    const max = Math.max(bs.checks, bl.checks);
    $("bars").append(bar("Binary Search", bs.checks, max, ""), bar("Linear", bl.checks, max, "lin"));
  }
  $("steps").replaceChildren(...bs.steps.map((s, n) =>
    row([n + 1, s.low, s.high, s.mid, { text: s.feasible ? "yes" : "no", cls: s.feasible ? "yes" : "no" }])));
}

async function loadHistory() {
  const rows = await (await fetch("/api/history")).json();
  $("history").replaceChildren(...rows.map((h) =>
    row([h.created, h.problem, h.answer, h.bs_checks, h.lin_checks ?? "skipped"])));
}

$("problem").addEventListener("change", refreshLabels);
$("example").addEventListener("click", () => {
  const m = META[$("problem").value];
  $("values").value = m.example[0];
  $("param").value = m.example[1];
});
$("form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const errs = $("errors");
  errs.hidden = true;
  const res = await fetch("/api/solve", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ problem: $("problem").value, values: $("values").value, param: $("param").value }),
  });
  const data = await res.json();
  if (!data.ok) {
    errs.replaceChildren(...data.errors.map((t) => { const li = document.createElement("li"); li.textContent = t; return li; }));
    errs.hidden = false;
    return;
  }
  showResult(data.result);
  loadHistory();
});

refreshLabels();
loadHistory();
