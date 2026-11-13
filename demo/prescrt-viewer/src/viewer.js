/* TOBI demo viewer for SCRT and pre-SCRT files.
 *
 * File contents can come from tested web pages and are untrusted: every value
 * is put on the page as text (textContent / createTextNode), never as HTML.
 * An image is shown only for a data:image/(png|jpeg|gif);base64 URL. No link
 * or URL is built from file data. View only: nothing is edited or saved. */
(function () {
  "use strict";

  var FORMAT = "pre-scrt/1";
  var RESULTS = ["Pass", "Fail", "Does Not Apply", "Not Tested"];
  var IMG_RE = /^data:image\/(png|jpeg|gif);base64,[A-Za-z0-9+/=\s]+$/;
  var NEEDS_TEXT = "Needs review: a person must decide";
  var NONE_TEXT = "No result recorded";
  var NOT_BY_TOBI = "Not tested by TOBI";
  var NOT_PERFORMED = "This test could not be performed";
  var state = { primary: null, compare: null };

  // ---- small helpers -------------------------------------------------------

  function txt(v) {
    if (v === null || v === undefined) return "";
    if (typeof v === "string") return v;
    if (typeof v === "number" || typeof v === "boolean") return String(v);
    try { return JSON.stringify(v); } catch (e) { return String(v); }
  }

  // SCRT writes empty as "" or " " (sometimes "undefined"), a newline as " \n ".
  function clean(v) {
    var s = txt(v);
    if (/^\s*(undefined|null)?\s*$/.test(s)) return "";
    return s.replace(/ \\n /g, "\n").replace(/\\n/g, "\n").trim();
  }

  function isObj(v) { return v !== null && typeof v === "object" && !Array.isArray(v); }

  // el("td", {class: "x"}, "text", node, ...): strings become text nodes.
  function el(tag, attrs) {
    var node = document.createElement(tag);
    if (attrs) {
      Object.keys(attrs).forEach(function (k) {
        if (attrs[k] === null || attrs[k] === undefined || attrs[k] === false) return;
        if (k === "text") node.textContent = attrs[k];
        else node.setAttribute(k, attrs[k] === true ? "" : String(attrs[k]));
      });
    }
    for (var i = 2; i < arguments.length; i++) add(node, arguments[i]);
    return node;
  }

  function add(node, child) {
    if (child === null || child === undefined || child === false) return;
    if (Array.isArray(child)) { child.forEach(function (c) { add(node, c); }); return; }
    node.appendChild(typeof child === "string" ? document.createTextNode(child) : child);
  }

  function orEmpty(s, empty) {
    return s ? document.createTextNode(s) : el("span", { class: "empty" }, empty || "(blank)");
  }

  // A long comment shows its start; the rest opens in place.
  function longText(s) {
    if (!s) return el("span", { class: "empty" }, "(blank)");
    if (s.length <= 450) return document.createTextNode(s);
    return el("details", { class: "more" }, el("summary", null, s.slice(0, 320) + "... ",
      el("span", { class: "morelink" }, "Show the whole comment")), s);
  }

  // ---- reading files -------------------------------------------------------

  function normalize(data) {
    if (Array.isArray(data)) {
      var rec = data[0];
      if (!isObj(rec) || !Array.isArray(rec.Criteria)) {
        throw new Error("This JSON is a list, but not an SCRT file: its first item has no Criteria rows.");
      }
      return fromScrt(rec);
    }
    if (isObj(data)) {
      if (data.format !== FORMAT) {
        throw new Error("This JSON is not a pre-SCRT file: it has no format \"pre-scrt/1\" field, and it is not an SCRT file (SCRT files are a list).");
      }
      if ("certified" in data && data.certified !== false) {
        throw new Error("This is not a valid pre-SCRT file: its \"certified\" field must be false.");
      }
      if (!Array.isArray(data.Criteria)) {
        throw new Error("This is not a valid pre-SCRT file: it has no Criteria rows.");
      }
      return fromPre(data);
    }
    throw new Error("This JSON is neither an SCRT file nor a pre-SCRT file.");
  }

  function baseRow(c, i) {
    if (!isObj(c)) throw new Error("Criteria row " + (i + 1) + " is not an object.");
    return {
      id: txt(c.TestID).replace(/\s+/g, ""),
      name: clean(c.TestName),
      test: clean(c.Test),
      crt: clean(c.CrtID),
      condition: clean(c.TestCondition),
      result: clean(c.TestResult) === "No Selection" ? "" : clean(c.TestResult),
      comment: clean(c.TesterComment),
      location: clean(c.location),
      global: clean(c.GlobalIssue),
      img: clean(c.ImageSrc),
      img2: clean(c.ImageSrc2),
      remediation: clean(c.RemediationDetails),
      remDate: clean(c.RemediationDate),
      needsReview: false,
      performed: true,
      parent: null,
      source: null,
      review: null
    };
  }

  function fromScrt(rec) {
    var first = {};
    var rows = rec.Criteria.map(function (c, i) {
      var r = baseRow(c, i);
      if (Object.prototype.hasOwnProperty.call(first, r.id)) r.parent = first[r.id];
      else first[r.id] = i;
      return r;
    });
    var s = isObj(rec.System) ? rec.System : {};
    return {
      kind: "scrt",
      product: isObj(rec.Product) ? rec.Product : {},
      tester: isObj(rec.Tester) ? rec.Tester : {},
      system: [
        ["Browser", clean(s.S_selectedBrowser)],
        ["Browser version", clean(s.S_selectedBrowserVersions)],
        ["Compatibility view", clean(s.S_Compatibility)],
        ["Operating system", clean(s.S_selectedOS)],
        ["Operating system version", clean(s.S_osVrsnNo)]
      ],
      rows: rows
    };
  }

  function fromPre(data) {
    var rows = data.Criteria.map(function (c, i) {
      var r = baseRow(c, i);
      r.needsReview = c.needs_review === true || r.result === "";
      r.source = isObj(c.source) ? c.source : null;
      r.performed = !(r.source && r.source.performed === false);
      r.review = isObj(c.review) ? c.review : null;
      var p = c.parent;
      r.parent = (typeof p === "number" && p >= 0 && p < i && p % 1 === 0) ? p : null;
      return r;
    });
    var s = isObj(data.System) ? data.System : {};
    var browsers = Array.isArray(s.browsers) ? s.browsers.map(function (b) {
      return isObj(b) ? (clean(b.name) + (clean(b.version) ? " " + clean(b.version) : "")) : clean(b);
    }) : [];
    var os = Array.isArray(s.os) ? s.os.map(clean) : [];
    return {
      kind: "pre",
      disclaimer: clean(data.disclaimer),
      origin: clean(data.origin),
      site: isObj(data.site) ? data.site : null,
      runs: Array.isArray(data.runs) ? data.runs : [],
      product: isObj(data.Product) ? data.Product : {},
      tester: isObj(data.Tester) ? data.Tester : {},
      system: [["Browsers", browsers.join(", ")], ["Operating systems", os.join(", ")]],
      rows: rows
    };
  }

  // ---- results -------------------------------------------------------------

  // A blank pre-SCRT result is one of two things: a test TOBI did not run
  // at all (no spec version and no spec rows: not one of its tests yet, or not
  // selected), or a test TOBI ran, or tried to, and left for a person.
  function inScope(row) {
    var s = row.source;
    return row.performed || !!(s && (clean(s.spec_version) || (Array.isArray(s.rows) && s.rows.length)));
  }

  function category(row, kind) {
    if (row.result === "") {
      if (kind !== "pre") return "none";
      return inScope(row) ? "needs" : "nottested";
    }
    return RESULTS.indexOf(row.result) >= 0 ? row.result : "other";
  }

  var CLASS_OF = { "Pass": "res-pass", "Fail": "res-fail", "Does Not Apply": "res-dna",
    "Not Tested": "res-nt", needs: "res-needs", none: "res-none", nottested: "res-none", other: "res-other" };

  function resultLabel(row, kind) {
    var cat = category(row, kind);
    if (cat === "needs") return NEEDS_TEXT;
    if (cat === "nottested") return NOT_BY_TOBI;
    if (cat === "none") return NONE_TEXT;
    if (cat === "other") return "Other: " + row.result;
    return cat;
  }

  // Why a blank row is blank, in a few words (the comment has the full reason).
  function whyNode(row, cat) {
    if (cat === "needs") {
      return el("span", { class: "why" }, row.performed ?
        "TOBI tested this and could not decide" : "TOBI could not complete this test");
    }
    if (cat === "nottested") {
      var c = row.comment;
      var why = /does not perform this test yet/.test(c) ? "Not one of TOBI's tests yet" :
        (/not selected for this run/.test(c) ? "Not selected for this run" : "TOBI did not run this test");
      return el("span", { class: "why quiet" }, why);
    }
    return null;
  }

  function resultNode(row, kind, isChild) {
    var cat = category(row, kind);
    var wrap = el("div", null, el("span", { class: "res " + CLASS_OF[cat] }, resultLabel(row, kind)));
    if (kind === "pre") {
      add(wrap, whyNode(row, cat));
      if (row.needsReview && row.result !== "") {
        add(wrap, el("span", { class: "flag" }, "Also marked as needing review by a person"));
      }
      if (row.review && row.review.checked === true) add(wrap, el("span", { class: "flag" }, "Checked by a person"));
      if (!isChild) {
        add(wrap, el("details", { class: "audit" }, el("summary", null, "Audit details"),
          sourceNode(row), el("div", { class: "small" }, el("b", null, "Person's review: "), reviewNode(row))));
      }
    }
    return wrap;
  }

  function needsPerson(row, kind) { return category(row, kind) === "needs"; }

  // ---- rendering -----------------------------------------------------------

  function fields(pairs) {
    var dl = el("dl", { class: "fields" });
    pairs.forEach(function (p) {
      add(dl, el("dt", null, p[0]));
      add(dl, el("dd", null, p[1] instanceof Node ? p[1] : orEmpty(clean(p[1]))));
    });
    return dl;
  }

  function block(title, summary, body, open) {
    return el("section", { class: "block" },
      el("h2", null, title),
      el("details", { open: !!open }, el("summary", { class: "collapsible" }, summary), body));
  }

  function tree(v) {
    if (Array.isArray(v)) {
      return el("ul", null, v.map(function (x) { return el("li", null, tree(x)); }));
    }
    if (isObj(v)) {
      return el("ul", null, Object.keys(v).map(function (k) {
        var val = v[k];
        return el("li", null, k + ": ", (isObj(val) || Array.isArray(val)) ? tree(val) : txt(val));
      }));
    }
    return document.createTextNode(txt(v));
  }

  function imageNode(value, alt) {
    if (!value) return el("span", { class: "empty" }, "None");
    if (IMG_RE.test(value)) {
      var img = el("img", { alt: alt });
      img.src = value; // checked above: a data: image only
      var btn = el("button", { type: "button", class: "thumb", "aria-label": alt + ": show larger" }, img);
      btn.addEventListener("click", function () { zoom(value, alt); });
      return btn;
    }
    var shown = value.length > 300 ? value.slice(0, 300) + "..." : value;
    return el("div", null, el("span", { class: "empty" }, "Not an inline image; shown as text: "),
      el("span", { class: "astext" }, shown));
  }

  function zoom(value, alt) {
    var d = document.getElementById("zoom");
    var img = document.getElementById("zoom-img");
    img.src = value;
    img.alt = alt;
    document.getElementById("zoom-title").textContent = alt;
    if (typeof d.showModal === "function") d.showModal();
  }

  function kv(label, value) {
    return el("div", { class: "kv" }, el("b", null, label + ": "), value instanceof Node ? value : txt(value));
  }

  function sourceNode(row) {
    var s = row.source;
    if (!s) return el("span", { class: "empty" }, "Not recorded");
    var by = clean(s.by);
    var out = el("div", { class: "small" },
      kv("By", by === "tool" ? "the tool" : (by === "person" ? "a person" : by || "(blank)")));
    if (clean(s.outcome)) add(out, kv("Tool's outcome", clean(s.outcome)));
    add(out, kv("Performed", s.performed === false ? el("strong", null, "No. " + NOT_PERFORMED) : "Yes"));
    if (clean(s.spec_version)) add(out, kv("Spec version", clean(s.spec_version)));
    if (Array.isArray(s.rows) && s.rows.length) add(out, kv("Spec rows", s.rows.map(clean).join(", ")));
    if (clean(s.decided_by)) add(out, kv("Decided by", clean(s.decided_by)));
    if (clean(s.run_id)) add(out, kv("Run", clean(s.run_id)));
    return out;
  }

  function reviewNode(row) {
    var r = row.review;
    if (!r) return el("span", { class: "empty" }, "none recorded");
    return el("div", { class: "small" },
      kv("Checked", r.checked === true ? "Yes" : "No"),
      kv("By", clean(r.by) || "(blank)"),
      kv("At", clean(r.at) || "(blank)"));
  }

  function compareMap(doc) {
    var map = {};
    doc.rows.forEach(function (r) {
      if (r.parent === null && !map[r.id]) map[r.id] = { row: r, children: 0 };
      else if (map[r.id]) map[r.id].children++;
    });
    return map;
  }

  function resultKey(row) { return row.result; }

  function renderReport() {
    var out = document.getElementById("report");
    out.textContent = "";
    var doc = state.primary && state.primary.doc;
    renderBanner();
    if (!doc) { out.hidden = true; return; }
    out.hidden = false;
    var pre = doc.kind === "pre";
    var cmp = state.compare && state.compare.doc;
    var p = doc.product, t = doc.tester;

    add(out, el("h2", null, "Report: " + (pre ? "pre-SCRT file (agent-assisted)" : "SCRT file (a person's record)")));
    add(out, el("p", { class: "intro" }, "Loaded from ", el("strong", null, state.primary.name),
      ". Page or product location: ", orEmpty(clean(p.P_Location))));

    add(out, block("Product", "Show Product section", fields([
      ["Product name", p.P_Name], ["Product version", p.P_Version], ["Product owner/vendor", p.P_Owner],
      ["Product type", p.P_Type], ["Location/URL", p.P_Location], ["Product description", p.P_Desc],
      ["Notes", p.P_Notes]])));
    add(out, block("Testing Information", "Show Testing Information section", fields([
      ["Company name", t.T_companyname], ["Tester's first name", t.T_fstnm], ["Tester's last name", t.T_lstnm],
      ["Trusted Tester ID", t.T_ID], ["Tester's email", t.T_cntc], ["Role", t.T_Role],
      ["Testing scope", t.T_scope], ["Testing method", t.T_eval], ["Testing method version", t.T_evalMthd_Vrsn],
      ["Date", t.T_Date]])));
    add(out, block("Test Environment", "Show Test Environment section", fields(doc.system)));

    if (pre) {
      var runs = el("div");
      if (!doc.runs.length) add(runs, el("p", { class: "empty" }, "No runs listed."));
      doc.runs.forEach(function (r, i) {
        r = isObj(r) ? r : {};
        add(runs, el("div", { class: "fields" },
          el("dt", null, "Run " + (i + 1)), el("dd", null, orEmpty(clean(r.run_id))),
          el("dt", null, "Report SHA-256"), el("dd", null, orEmpty(clean(r.report_sha256))),
          el("dt", null, "Versions"), el("dd", null, el("details", null,
            el("summary", null, "Show versions recorded for this run"), el("div", { class: "tree" }, tree(r.versions || {}))))));
      });
      var site = doc.site;
      add(out, block("Record details (pre-SCRT)", "Show record details", el("div", null, fields([
        ["Format", FORMAT],
        ["Origin (the format it was read from)", doc.origin],
        ["Disclaimer", doc.disclaimer],
        ["Site name", site ? site.name : ""],
        ["Site pages", site && Array.isArray(site.pages) && site.pages.length ?
          el("ul", null, site.pages.map(function (x) { return el("li", null, clean(x)); })) : ""]
      ]), el("h3", null, "Runs"), runs), true));
    }

    renderResults(out, doc, cmp);
  }

  function renderResults(out, doc, cmp) {
    var pre = doc.kind === "pre";
    add(out, el("h2", { id: "h-results" }, "Test Results"));

    // Summary: counts over tests (rows that are not child issues). Counting only.
    var counts = {}, children = 0;
    doc.rows.forEach(function (r) {
      if (r.parent !== null) { children++; return; }
      var c = category(r, doc.kind);
      counts[c] = (counts[c] || 0) + 1;
    });
    var items = [["Pass", "Pass"], ["Fail", "Fail"], ["Does Not Apply", "Does Not Apply"], ["Not Tested", "Not Tested"]];
    if (pre) items.push(["needs", "Needs review (TOBI ran or tried the test)"], ["nottested", NOT_BY_TOBI]);
    else items.push(["none", NONE_TEXT]);
    if (counts.other) items.push(["other", "Other values"]);
    var ul = el("ul", { class: "summary", "aria-label": "Counts of tests by result" });
    items.forEach(function (it) {
      add(ul, el("li", null, el("span", { class: "n" }, String(counts[it[0]] || 0)), it[1]));
    });
    add(ul, el("li", null, el("span", { class: "n" }, String(children)), "Child issue rows"));
    add(out, el("p", { class: "intro" }, "Counts are of tests; child issue rows are counted apart. These are counts only, not a score."));
    add(out, ul);

    var cmap = cmp ? compareMap(cmp) : null;
    if (cmp) {
      var a = clean(doc.product.P_Location), b = clean(cmp.product.P_Location);
      add(out, el("p", { class: "intro" }, "Compared with ", el("strong", null, state.compare.name),
        " (" + (cmp.kind === "pre" ? "pre-SCRT file" : "SCRT file") + "), matched by test ID."));
      if (a && b && a !== b) {
        add(out, el("p", { class: "note" }, "The two files name different locations: ", el("strong", null, a),
          " and ", el("strong", null, b), ". They may not be records of the same page."));
      }
    }

    // Filters and column choices.
    var sel = el("select", { id: "filter-result" });
    [["all", "All results"], ["Pass", "Pass"], ["Fail", "Fail"], ["Does Not Apply", "Does Not Apply"],
      ["Not Tested", "Not Tested"]]
      .concat(pre ? [["needs", "Needs review"], ["nottested", NOT_BY_TOBI]] : [["none", NONE_TEXT]])
      .forEach(function (o) { add(sel, el("option", { value: o[0] }, o[1])); });
    var chkPerson = pre ? el("input", { type: "checkbox", id: "filter-person" }) : null;
    var chkDiff = cmp ? el("input", { type: "checkbox", id: "filter-differs" }) : null;
    var chkCompact = cmp ? el("input", { type: "checkbox", id: "view-compact", checked: true }) : null;
    var chkRem = el("input", { type: "checkbox", id: "view-remediation" });
    function opt(chk, text) { return chk ? el("span", null, chk, " ", el("label", { for: chk.id }, text)) : null; }
    add(out, el("div", { class: "filters" },
      el("span", null, el("label", { for: "filter-result" }, "Filter results by: "), sel),
      opt(chkPerson, "Only needs review"),
      opt(chkDiff, "Only tests whose results differ")));
    add(out, el("div", { class: "filters" },
      opt(chkCompact, "Compare view: fewer columns, to fit the screen (untick for every column of the report file)"),
      opt(chkRem, "Show remediation columns")));
    var shown = el("p", { id: "shown", role: "status", "aria-live": "polite" });
    add(out, shown);

    // Table. Each cell carries its column's class so a view can hide columns.
    var cols = [["id", "Test ID"], ["row", "Row"], ["name", "Test name"], ["cond", "Test condition"],
      ["result", pre ? "Test result (TOBI)" : "Test result"], ["comment", "Comments"], ["shot", "Screenshot"]];
    if (cmp) cols.push(["cres", "Compare file: result"], ["ccom", "Compare file: comments"], ["diff", "Same or differs"]);
    cols.push(["loc", "Location/screen"], ["global", "Global issue"],
      ["rem", "Remediation details"], ["rem", "Remediation screenshot"], ["rem", "Remediation date"]);
    var thead = el("thead", null, el("tr", null, cols.map(function (c) {
      return el("th", { scope: "col", class: "c-" + c[0] + (/^(cres|ccom|diff)$/.test(c[0]) ? " cmp" : "") }, c[1]);
    })));
    var tbody = el("tbody");
    var groups = [];
    var childNo = {};

    doc.rows.forEach(function (r, i) {
      var isChild = r.parent !== null;
      var tr = el("tr", { class: isChild ? "child" : null });
      var label;
      if (isChild) {
        childNo[r.parent] = (childNo[r.parent] || 0) + 1;
        label = "Child issue " + childNo[r.parent] + " of row " + (r.parent + 1);
      } else label = "Row " + (i + 1);
      add(tr, el("th", { scope: "row", class: "c-id" }, r.id || "(no test ID)",
        isChild ? el("div", { class: "small childmark" }, "↳ child issue " + childNo[r.parent]) : null));
      add(tr, el("td", { class: "c-row small" }, (isChild ? "↳ " : "") + label));
      add(tr, el("td", { class: "c-name" }, orEmpty(r.name), r.crt ? el("div", { class: "small" }, "Criteria: " + r.crt) : null));
      add(tr, el("td", { class: "c-cond pre" }, orEmpty(r.condition)));
      add(tr, el("td", { class: "c-result" }, resultNode(r, doc.kind, isChild)));
      add(tr, el("td", { class: "c-comment pre" }, longText(r.comment),
        r.location ? el("div", { class: "where" }, el("b", null, "Where: "), r.location) : null));
      add(tr, el("td", { class: "c-shot" }, imageNode(r.img, "Screenshot for test " + r.id + ", " + label.toLowerCase())));
      var differs = false;
      if (cmp) {
        if (isChild) {
          add(tr, el("td", { class: "cmpcell c-cres", colspan: 3 }, el("span", { class: "empty" }, "See the test row above")));
        } else {
          var m = cmap[r.id];
          if (!m) {
            add(tr, el("td", { class: "cmpcell c-cres", colspan: 3 }, el("span", { class: "empty" }, "Not in the compare file")));
          } else {
            differs = resultKey(m.row) !== resultKey(r);
            add(tr, el("td", { class: "cmpcell c-cres" }, resultNode(m.row, cmp.kind, false)));
            add(tr, el("td", { class: "cmpcell c-ccom pre" }, longText(m.row.comment),
              m.row.location ? el("div", { class: "where show" }, el("b", null, "Where: "), m.row.location) : null,
              m.row.img ? el("div", null, imageNode(m.row.img, "Compare file's screenshot for test " + r.id)) : null,
              m.children ? el("div", { class: "small" }, "Plus " + m.children + " child issue row" + (m.children > 1 ? "s" : "") + " in the compare file") : null));
            add(tr, el("td", { class: "cmpcell c-diff" }, differs ?
              el("span", { class: "differs-mark" }, "≠ Differs") : "Same result"));
            if (differs) tr.classList.add("differs");
          }
        }
      }
      add(tr, el("td", { class: "c-loc" }, orEmpty(r.location)));
      add(tr, el("td", { class: "c-global" }, orEmpty(r.global)));
      add(tr, el("td", { class: "c-rem pre" }, orEmpty(r.remediation)));
      add(tr, el("td", { class: "c-rem" }, imageNode(r.img2, "Remediation screenshot for test " + r.id + ", " + label.toLowerCase())));
      add(tr, el("td", { class: "c-rem" }, orEmpty(r.remDate)));

      tbody.appendChild(tr);
      if (!isChild) groups.push({ row: r, trs: [tr], differs: differs });
      else {
        for (var g = groups.length - 1; g >= 0; g--) {
          if (groups[g].row === doc.rows[r.parent]) { groups[g].trs.push(tr); break; }
        }
      }
    });

    var table = el("table", { id: "results", class: "table" },
      el("caption", null, el("strong", null, "View results")), thead, tbody);
    add(out, el("div", { class: "tablewrap", tabindex: "0", role: "region", "aria-labelledby": "h-results" }, table));

    if (cmp) {
      var ids = {};
      doc.rows.forEach(function (r) { ids[r.id] = true; });
      var only = Object.keys(cmap).filter(function (k) { return !ids[k]; });
      if (only.length) {
        add(out, el("h3", null, "Tests only in the compare file"));
        add(out, el("ul", { class: "plain" }, only.map(function (k) {
          return el("li", null, k + ": ", el("span", { class: "res " + CLASS_OF[category(cmap[k].row, cmp.kind)] }, resultLabel(cmap[k].row, cmp.kind)));
        })));
      }
    }

    function apply() {
      var f = sel.value, onlyPerson = chkPerson && chkPerson.checked, onlyDiff = chkDiff && chkDiff.checked;
      var n = 0;
      groups.forEach(function (g) {
        var r = g.row, ok = true;
        if (f !== "all") ok = category(r, doc.kind) === f;
        if (onlyPerson && !needsPerson(r, doc.kind)) ok = false;
        if (onlyDiff && !g.differs) ok = false;
        g.trs.forEach(function (tr) { tr.hidden = !ok; if (ok) n++; });
      });
      shown.textContent = "Showing " + n + " of " + doc.rows.length + " rows.";
    }
    function view() {
      table.classList.toggle("compact", !!(chkCompact && chkCompact.checked));
      table.classList.toggle("norem", !chkRem.checked);
    }
    if (chkCompact) chkCompact.addEventListener("change", view);
    chkRem.addEventListener("change", view);
    view();
    sel.addEventListener("change", apply);
    if (chkPerson) chkPerson.addEventListener("change", apply);
    if (chkDiff) chkDiff.addEventListener("change", apply);
    apply();
  }

  function renderBanner() {
    var b = document.getElementById("banner");
    b.textContent = "";
    var files = [];
    if (state.primary) files.push(["Report file", state.primary]);
    if (state.compare) files.push(["Compare file", state.compare]);
    var anyPre = files.some(function (f) { return f[1].doc.kind === "pre"; });
    b.className = "banner " + (anyPre ? "warn" : "neutral");
    if (!files.length) {
      add(b, el("p", null, "No file loaded yet. This viewer shows SCRT and pre-SCRT files; it does not test pages."));
      return;
    }
    files.forEach(function (f) {
      var d = f[1].doc;
      if (d.kind === "pre") {
        add(b, el("p", null, el("span", { class: "kind" }, f[0] + " (" + f[1].name + "): pre-SCRT file. "),
          "This is an agent-assisted record made by a tool, not a Trusted Tester's record. ",
          d.disclaimer ? ["The file's disclaimer: ", el("q", null, d.disclaimer)] : "The file has no disclaimer text."));
      } else {
        add(b, el("p", null, el("span", { class: "kind" }, f[0] + " (" + f[1].name + "): SCRT file. "),
          "This is a person's SCRT record, shown as loaded."));
      }
    });
  }

  // ---- loading -------------------------------------------------------------

  function showError(msg) { document.getElementById("error").textContent = msg; }
  function showStatus(msg) { document.getElementById("status").textContent = msg; }

  function load(file, slot) {
    if (!file) return;
    var reader = new FileReader();
    reader.onload = function () {
      var doc;
      try {
        var data;
        try { data = JSON.parse(String(reader.result)); } catch (e) { throw new Error("This file is not JSON, so it is neither an SCRT file nor a pre-SCRT file."); }
        doc = normalize(data);
      } catch (e) {
        state[slot] = null;
        if (slot === "primary") state.compare = null;
        document.getElementById("clear-compare").hidden = !state.compare;
        showStatus("");
        showError((slot === "primary" ? "Report file" : "Compare file") + " \"" + file.name + "\" was not loaded. " + e.message);
        renderReport();
        return;
      }
      state[slot] = { name: file.name, doc: doc };
      showError("");
      document.getElementById("clear-compare").hidden = !state.compare;
      var kind = doc.kind === "pre" ? "a pre-SCRT file (agent-assisted record)" : "an SCRT file (a person's record)";
      showStatus((slot === "primary" ? "Report file" : "Compare file") + " loaded: \"" + file.name + "\" is " + kind +
        " with " + doc.rows.length + " rows." + (slot === "compare" && !state.primary ? " Choose a report file to see it." : ""));
      renderReport();
    };
    reader.onerror = function () { showError("The file could not be read."); };
    reader.readAsText(file);
  }

  function wire(inputId, zoneId, slot) {
    var input = document.getElementById(inputId), zone = document.getElementById(zoneId);
    input.addEventListener("change", function () { load(input.files[0], slot); });
    zone.addEventListener("dragover", function (e) { e.preventDefault(); zone.classList.add("over"); });
    zone.addEventListener("dragleave", function () { zone.classList.remove("over"); });
    zone.addEventListener("drop", function (e) {
      e.preventDefault();
      zone.classList.remove("over");
      if (e.dataTransfer && e.dataTransfer.files.length) load(e.dataTransfer.files[0], slot);
    });
  }

  // A file dropped outside the boxes must not open in the tab.
  window.addEventListener("dragover", function (e) { e.preventDefault(); });
  window.addEventListener("drop", function (e) { e.preventDefault(); });

  wire("primary-file", "drop-primary", "primary");
  wire("compare-file", "drop-compare", "compare");
  document.getElementById("clear-compare").addEventListener("click", function () {
    state.compare = null;
    document.getElementById("compare-file").value = "";
    document.getElementById("clear-compare").hidden = true;
    showStatus("Compare file removed.");
    renderReport();
  });
  document.getElementById("zoom-close").addEventListener("click", function () {
    document.getElementById("zoom").close();
  });
})();
