// Field Card front-end: sends your details to the local model and draws the printable card.
const $ = (id) => document.getElementById(id);
let model = "";

// Remember the region between visits. It is saved in this browser only.
$("region").value = localStorage.getItem("fieldcard-region") || "";

// Small helper: make an element with a class and text (textContent keeps it safe).
function h(tag, cls, text) {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (text) e.textContent = text;
  return e;
}
function list(items, cls) {
  const ul = h("ul", cls);
  items.forEach((t) => ul.appendChild(h("li", "", String(t))));
  return ul;
}
function hint(text) {
  $("preview").replaceChildren(h("div", "hint", text));
}

// Asks the server if Ollama is running and the model is downloaded.
async function checkStatus() {
  const s = await (await fetch("/api/status")).json();
  model = s.model;
  $("model").textContent = s.model;
  $("dot").className = "dot " + (s.state === "ready" ? "ready" : "bad");
  $("notice").style.display = s.message ? "block" : "none";
  $("notice").textContent = s.message || "";
}

// Builds the printable card on screen.
function render(c, d) {
  const sheet = h("article", "sheet");
  sheet.append(
    h("p", "date", d.today), h("h2", "", c.title), h("p", "intro", c.intro),
    h("h3", "", "Bring"), list(c.bring, "plain"),
    h("h3", "", "Find these"), list(c.notice, "checks"),
    h("h3", "", "Phone rule"), h("p", "", c.phone_rule),
    h("h3", "", "On the way back"), h("p", "", c.on_the_way_back),
    h("p", "foot", `Written offline on this laptop by ${model}.`)
  );
  const actions = h("div", "actions");
  const print = h("button", "go", "Print or save as PDF");
  print.onclick = () => window.print();   // Windows lets you pick "Microsoft Print to PDF"
  actions.append(print);
  $("preview").replaceChildren(sheet, actions);
}

$("form").addEventListener("submit", async (e) => {
  e.preventDefault();
  localStorage.setItem("fieldcard-region", $("region").value);
  const d = {
    region: $("region").value.trim(),
    place: $("place").value,
    minutes: Number($("minutes").value),
    who: $("who").value,
    note: $("note").value.trim(),
    today: new Date().toLocaleDateString("en-GB", { day: "numeric", month: "long", year: "numeric" }),
  };
  $("go").disabled = true;
  $("go").textContent = "Writing your card…";
  hint("Writing your card. On a laptop this takes about 10 to 40 seconds.");
  try {
    const res = await fetch("/api/card", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(d) });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error);
    render(data, d);
  } catch (err) {
    hint(err.message || "Something went wrong. Is the Field Card window still open?");
    checkStatus();
  }
  $("go").disabled = false;
  $("go").textContent = "Make my card";
});

hint("Your card shows up here. Print it, pocket the phone, go.");
checkStatus();
