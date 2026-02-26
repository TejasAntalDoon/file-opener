import streamlit as st
import fitz
import requests
import base64
import json
import streamlit.components.v1 as components

st.set_page_config(page_title="PDF Vocabulary Reader", layout="wide")

for k, v in [("pdf_bytes", None)]:
    if k not in st.session_state:
        st.session_state[k] = v

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.header("📚 Word Meaning")
st.sidebar.markdown(
    '<div id="meaning-box" style="font-family:sans-serif;font-size:14px;'
    'line-height:1.6;color:#333333;padding:4px 0;background:transparent">'
    'Click any word in the PDF to see its meaning here.</div>',
    unsafe_allow_html=True
)

# ── Global responsive CSS ─────────────────────────────────────────────────────
st.markdown("""
<style>
/* Make Streamlit layout fill full height on mobile */
html, body, [data-testid="stAppViewContainer"] {
    height: 100%;
}
/* Tighten sidebar on mobile */
@media (max-width: 768px) {
    [data-testid="stSidebar"] {
        min-width: 0 !important;
        width: 100% !important;
    }
    [data-testid="stSidebar"] > div {
        padding: 0.5rem !important;
    }
}
</style>
""", unsafe_allow_html=True)

# ── Title ─────────────────────────────────────────────────────────────────────
st.title("📖 Smart PDF Vocabulary Reader")
st.write("Upload a PDF and click any word to see its meaning in the sidebar.")

# ── File uploader ─────────────────────────────────────────────────────────────
uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])
if uploaded_file is not None:
    new_bytes = uploaded_file.read()
    if new_bytes != st.session_state.pdf_bytes:
        st.session_state.pdf_bytes = new_bytes

# ── Render PDF ────────────────────────────────────────────────────────────────
if st.session_state.pdf_bytes:
    doc = fitz.open(stream=st.session_state.pdf_bytes, filetype="pdf")
    total_pages = len(doc)
    st.success(f"Loaded PDF — {total_pages} page(s). Scroll to read.")

    all_pages = []
    for i in range(total_pages):
        page = doc[i]
        pw, ph = page.rect.width, page.rect.height
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        img_b64 = base64.b64encode(pix.tobytes("png")).decode()
        words = []
        for w in page.get_text("words"):
            x0, y0, x1, y1, txt = w[0], w[1], w[2], w[3], w[4]
            clean = txt.strip(".,!?;:\"'()[]{}<>-•").lower()
            if clean and any(c.isalpha() for c in clean):
                words.append({
                    "x0": round(x0/pw, 5), "y0": round(y0/ph, 5),
                    "x1": round(x1/pw, 5), "y1": round(y1/ph, 5),
                    "word": clean
                })
        all_pages.append({"img": img_b64, "words": words, "aspect": round(ph/pw, 4)})
    doc.close()

    pages_json = json.dumps(all_pages)

    html = f"""<!DOCTYPE html>
<html><head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  html, body {{ height: 100%; overflow: hidden; background: #5a5a5a; }}

  #viewer {{
    height: 100vh;
    overflow-y: scroll;
    padding: 12px 8px;
    -webkit-overflow-scrolling: touch;
  }}

  .page-wrap {{
    position: relative;
    width: 100%;
    max-width: 860px;
    margin: 0 auto 14px auto;
    background: white;
    box-shadow: 0 3px 16px rgba(0,0,0,.45);
    border-radius: 2px;
  }}
  .page-wrap img {{ width: 100%; display: block; border-radius: 2px; }}

  .placeholder {{
    width: 100%;
    background: #ececec;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #bbb;
    font-size: 13px;
    font-family: sans-serif;
    border-radius: 2px;
  }}

  .w {{
    position: absolute;
    cursor: pointer;
    border-radius: 2px;
    transition: background .08s;
    /* Larger tap target on mobile */
    min-width: 10px;
    min-height: 14px;
  }}
  .w:hover {{ background: rgba(255,235,59,.5); }}
  .w.on {{ background: rgba(255,193,7,.8); outline: 2px solid #e65100; }}

  /* Mobile meaning popup — shown inside viewer on small screens */
  #mobile-popup {{
    display: none;
    position: fixed;
    bottom: 0; left: 0; right: 0;
    background: white;
    border-top: 3px solid #ffc107;
    padding: 14px 18px 20px;
    box-shadow: 0 -4px 20px rgba(0,0,0,.3);
    z-index: 1000;
    font-family: sans-serif;
    max-height: 45vh;
    overflow-y: auto;
  }}
  #mobile-popup h3 {{
    font-size: 16px; margin-bottom: 6px; color: #1a1a1a;
  }}
  #mobile-popup p {{
    font-size: 14px; line-height: 1.6; color: #444;
  }}
  #popup-close {{
    position: absolute; top: 10px; right: 14px;
    font-size: 20px; cursor: pointer; color: #888;
    background: none; border: none; line-height: 1;
  }}

  @media (max-width: 600px) {{
    #viewer {{ padding: 8px 4px; }}
    .page-wrap {{ margin-bottom: 10px; }}
  }}
</style>
</head>
<body>
<div id="viewer">
  <div id="container"></div>
</div>

<!-- Mobile bottom sheet for meaning -->
<div id="mobile-popup">
  <button id="popup-close" onclick="closePopup()">✕</button>
  <h3 id="popup-word"></h3>
  <p id="popup-defn"></p>
</div>

<script>
var pages  = {pages_json};
var viewer = document.getElementById("viewer");
var isMobile = window.innerWidth <= 768;

window.addEventListener("resize", function() {{
  isMobile = window.innerWidth <= 768;
}});

function closePopup() {{
  document.getElementById("mobile-popup").style.display = "none";
}}

function showMeaning(word) {{
  if (isMobile) {{
    // On mobile: show bottom popup inside the iframe
    var popup = document.getElementById("mobile-popup");
    var wEl   = document.getElementById("popup-word");
    var dEl   = document.getElementById("popup-defn");
    wEl.textContent = word;
    dEl.textContent = "Looking up...";
    popup.style.display = "block";

    fetch("https://api.dictionaryapi.dev/api/v2/entries/en/" + encodeURIComponent(word))
      .then(function(r) {{ return r.json(); }})
      .then(function(data) {{
        var defn = getDefn(data);
        dEl.textContent = defn;
      }})
      .catch(function() {{ dEl.textContent = "Error fetching meaning."; }});

  }} else {{
    // On desktop: write into Streamlit sidebar div
    var box = window.parent.document.getElementById("meaning-box");
    if (!box) return;
    box.innerHTML = '<span style="color:#888;font-style:italic;font-family:sans-serif">Looking up <b>' + word + '</b>...</span>';

    fetch("https://api.dictionaryapi.dev/api/v2/entries/en/" + encodeURIComponent(word))
      .then(function(r) {{ return r.json(); }})
      .then(function(data) {{
        var defn = getDefn(data);
        box.innerHTML =
          '<h3 style="margin-bottom:8px;font-family:sans-serif;font-size:16px;color:#1a1a1a;background:transparent">' + word + '</h3>' +
          '<p style="font-family:sans-serif;font-size:14px;line-height:1.65;color:#333333;background:transparent">' + defn + '</p>';
      }})
      .catch(function() {{
        box.innerHTML = '<p style="color:red;font-family:sans-serif;font-size:13px">Error fetching meaning.</p>';
      }});
  }}
}}

function getDefn(data) {{
  if (!Array.isArray(data) || !data[0] || !data[0].meanings) return "No definition found.";
  var meanings = data[0].meanings;
  for (var i = 0; i < meanings.length; i++) {{
    var defs = meanings[i].definitions;
    if (defs && defs.length > 0 && defs[0].definition) return defs[0].definition;
  }}
  return "No definition found.";
}}

function layOverlays(wrap, idx) {{
  wrap.querySelectorAll(".w").forEach(function(e) {{ e.remove(); }});
  var img = wrap.querySelector("img");
  if (!img) return;
  var W = img.clientWidth, H = img.clientHeight;
  pages[idx].words.forEach(function(w) {{
    var d = document.createElement("div");
    d.className = "w";
    d.style.left   = (w.x0 * W) + "px";
    d.style.top    = (w.y0 * H) + "px";
    d.style.width  = ((w.x1 - w.x0) * W) + "px";
    d.style.height = ((w.y1 - w.y0) * H) + "px";
    (function(word) {{
      d.onclick = function() {{
        document.querySelectorAll(".w.on").forEach(function(e) {{ e.classList.remove("on"); }});
        d.classList.add("on");
        showMeaning(word);
      }};
    }})(w.word);
    wrap.appendChild(d);
  }});
}}

function loadPage(wrap, idx) {{
  if (wrap.dataset.loaded === "1") return;
  wrap.dataset.loaded = "1";
  var img = document.createElement("img");
  img.onload = function() {{
    var ph = wrap.querySelector(".placeholder");
    if (ph) wrap.removeChild(ph);
    layOverlays(wrap, idx);
  }};
  img.src = "data:image/png;base64," + pages[idx].img;
  wrap.appendChild(img);
  pages[idx].img = null;
}}

var container = document.getElementById("container");
pages.forEach(function(p, idx) {{
  var wrap = document.createElement("div");
  wrap.className = "page-wrap";
  wrap.id = "pg" + idx;
  var ph = document.createElement("div");
  ph.className = "placeholder";
  ph.style.height = Math.round(wrap.offsetWidth || 800) * p.aspect + "px";
  ph.textContent = "Page " + (idx + 1) + " of " + pages.length;
  wrap.appendChild(ph);
  container.appendChild(wrap);
}});

var obs = new IntersectionObserver(function(entries) {{
  entries.forEach(function(e) {{
    if (!e.isIntersecting) return;
    var idx = parseInt(e.target.id.replace("pg", ""));
    loadPage(e.target, idx);
    var nxt = document.getElementById("pg" + (idx + 1));
    if (nxt) loadPage(nxt, idx + 1);
  }});
}}, {{ root: viewer, rootMargin: "400px" }});

document.querySelectorAll(".page-wrap").forEach(function(el) {{ obs.observe(el); }});

window.addEventListener("resize", function() {{
  document.querySelectorAll(".page-wrap").forEach(function(wrap, idx) {{
    if (wrap.dataset.loaded === "1") layOverlays(wrap, idx);
  }});
}});
</script>
</body></html>"""

    components.html(html, height=860, scrolling=False)