"""
Wreck & Roll site updater. No installs needed (Python 3 only).

What it does, for every .html page in this folder:
  1. Rebuilds the header from partials/header.html and the menu in partials/nav.json
     (the current page's link is highlighted automatically).
  2. Rebuilds the footer from partials/footer.html.
  3. Rebuilds the lists on /guides/ and /case-studies/ from the pages in those folders
     (title = the page's <h1>, summary = its meta description).

How to use:
  - To change the menu: edit partials/nav.json.
  - To change the footer: edit partials/footer.html.
  - To add a page: copy any page, change its content, put it in its own folder.
  - Then run:  python update_site.py   and upload the changed files.
"""
import html, json, os, re

ROOT = os.path.dirname(os.path.abspath(__file__))
SKIP = {"partials", ".git"}
# Folders whose index page lists every page inside them: folder -> link text
LISTS = {"guides": "Read the guide", "case-studies": "Read the case study"}

def read(p):
    with open(os.path.join(ROOT, p), encoding="utf-8") as f:
        return f.read()

def page_url(rel):
    rel = rel.replace(os.sep, "/")
    if rel == "index.html":
        return "/"
    if rel.endswith("/index.html"):
        return "/" + rel[: -len("index.html")]
    return "/" + rel

def nav_html(url, items):
    out = []
    for it in items:
        on = url == it["url"] or ("match" in it and url.startswith(it["match"]))
        cur = ' aria-current="page"' if on else ""
        out.append(f'      <a href="{it["url"]}"{cur}>{html.escape(it["title"])}</a>')
    return "\n".join(out)

def list_html(pages, folder, more):
    cards = []
    for rel, text in sorted(pages):
        if not rel.startswith(folder + "/") or rel == folder + "/index.html":
            continue
        h1 = re.search(r"<h1[^>]*>(.*?)</h1>", text, re.S)
        desc = re.search(r'<meta name="description" content="([^"]*)"', text)
        title = re.sub(r"<[^>]+>", "", h1.group(1)).strip() if h1 else rel
        summary = desc.group(1) if desc else ""
        cards.append(
            f'  <a class="guide-card" href="{page_url(rel)}"><h2>{title}</h2>'
            f"<p>{summary}</p><span>{more}</span></a>"
        )
    return "\n".join(cards)

def main():
    header = read("partials/header.html").rstrip("\n")
    footer = read("partials/footer.html").rstrip("\n")
    nav = json.loads(read("partials/nav.json"))["nav"]

    pages = []
    for d, dirs, files in os.walk(ROOT):
        dirs[:] = [x for x in dirs if x not in SKIP]
        for f in files:
            if f.endswith(".html"):
                rel = os.path.relpath(os.path.join(d, f), ROOT).replace(os.sep, "/")
                pages.append((rel, read(rel)))

    changed = 0
    for rel, text in pages:
        new = text
        h = header.replace("{{NAV}}", nav_html(page_url(rel), nav))
        new = re.sub(r'<header class="site-header">.*?</header>', lambda m: h, new, count=1, flags=re.S)
        new = re.sub(r'<footer class="site-footer">.*?(?=\n?</body>)', lambda m: footer, new, count=1, flags=re.S)
        for folder, more in LISTS.items():
            if rel == folder + "/index.html":
                new = re.sub(r"<!-- LIST:" + folder + r":START -->.*?<!-- LIST:" + folder + r":END -->",
                             lambda m: f"<!-- LIST:{folder}:START -->\n" + list_html(pages, folder, more) + f"\n<!-- LIST:{folder}:END -->",
                             new, count=1, flags=re.S)
        if new != text:
            with open(os.path.join(ROOT, rel), "w", encoding="utf-8") as f:
                f.write(new)
            changed += 1
            print("updated", rel)
    print(f"Done. {changed} file(s) changed.")

if __name__ == "__main__":
    main()
