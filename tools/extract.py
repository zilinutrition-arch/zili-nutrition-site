#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
One-time extractor: turns the current single-file site (index.html) into
  - templates/index.html   (same file, editable TEXT NODES replaced by {{path}} placeholders;
                            tags/attributes stay inside the template)
  - content/*.json         (initial values: user-readable text only, entities unescaped)

PLAN entry: (json_file, dotted_path, shell_before, editable_text, shell_after, kind)
  - shell_before + editable_text + shell_after must equal the exact source fragment.
  - kind "text": value stored as the raw text node (html.unescape applied), build escapes it
                 back (so the initial build is byte-identical AND user input like `&` is safe).
  - kind "html": value stored verbatim (fragment may contain real markup/entities), build
                 injects it as-is.
Every entry asserts the occurrence count of the whole fragment, catching typos or drift.
"""
import html
import json
import pathlib
import re
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "index.html"
TPL = ROOT / "templates" / "index.html"
OUT = ROOT / "content"

# ----------------------------------------------------------------- mapping ---
PLAN = [
    # ---------------- settings.json ----------------
    ("settings", "meta.title", "<title>", "Zili Nutrition — Private-Label Dietary Supplements (Wholesale · OEM · ODM)", "</title>", "text"),
    ("settings", "meta.description", '<meta name="description" content="', "Zili Nutrition — private-label dietary supplement manufacturer offering wholesale, OEM and ODM services for Europe, the United States and Southeast Asia.", '">', "text"),
    ("settings", "brand_name", '<span>', "Zili Nutrition", "</span>", "text"),  # header + footer brands
    ("settings", "nav_home", '>', "Home", "</a>", "text"),  # header nav + footer site list
    ("settings", "nav_about", '>', "About", "</a>", "text"),
    ("settings", "nav_products", '>', "Products", "</a>", "text"),
    ("settings", "nav_oem", '>', "OEM / ODM", "</a>", "text"),
    ("settings", "nav_contact", '>', "Contact", "</a>", "text"),
    ("settings", "cta_quote", '>', "Request a Quote", "</a>", "text"),  # header, hero, footer CTA
    ("settings", "sample_tag", '<span class="tag">', "Sample", "</span>", "text"),  # 9 tags
    ("settings", "sample_notice",
     '<span><strong>', "Sample concept site.", '</strong> Company identity and contacts are real; certifications, product specifics and performance numbers remain placeholders — verify them before publishing.</span>',
     "html"),
    ("settings", "footer_desc",
     '<p class="footer-desc">',
     "Zili Nutrition (Zhengzhou, China) — private-label dietary supplement manufacturer serving wholesalers, brands and importers across Europe, the United States and Southeast Asia. Certifications, product specifics and performance numbers remain placeholders pending verification.",
     "</p>", "text"),
    ("settings", "footer_site_title", "<h4>", "Site", "</h4>", "text"),
    ("settings", "footer_contact_title", "<h4>", "Contact", "</h4>", "text"),
    ("settings", "footer_copyright", "© <span id=\"year\">", "2026", "</span> ", "text"),
    ("settings", "footer_company", "", "Zili Nutrition", ". All rights reserved.", "text"),
    ("settings", "footer_privacy", ">", "Privacy (Sample)", "</a>", "text"),
    ("settings", "footer_terms", ">", "Terms (Sample)", "</a>", "text"),
    ("settings", "footer_accessibility", ">", "Accessibility", "</a>", "text"),
    # ---------------- home.json (hero) ----------------
    ("home", "hero.eyebrow", '<span class="section-eyebrow">', "Wholesale · OEM · ODM", "</span>", "text"),
    ("home", "hero.title1", '<h1 id="home-title">', "Private-Label Dietary Supplements,", "<br><span class=\"accent\">", "html"),
    ("home", "hero.title2", "", "Built for Global Partners.", "</span></h1>", "text"),
    ("home", "hero.lead", '<p class="hero-lead">',
     "Zili Nutrition develops and produces private-label supplements — capsules, tablets, powders, gummies and softgels — for wholesalers and brands selling into Europe, the United States and Southeast Asia.",
     "</p>", "text"),
    ("home", "hero.cta_secondary", '>', "View Product Lines", "</a>", "text"),
    ("home", "hero.sample_note", "", "Sample copy — replace with verified brand positioning and credentials.", "", "text"),
    ("home", "hero.proof_title", "<h3>", "Coverage (Sample)", "</h3>", "text"),
    ("home", "hero.proof0.title", "<strong>", "Europe", "</strong><span>", "text"),
    ("home", "hero.proof0.text", "", "Wholesale &amp; private label", "</span>", "text"),
    ("home", "hero.proof1.title", "<strong>", "United States", "</strong><span>", "text"),
    ("home", "hero.proof1.text", "", "OEM &amp; ODM programs", "</span>", "text"),
    ("home", "hero.proof2.title", "<strong>", "Southeast Asia", "</strong><span>", "text"),
    ("home", "hero.proof2.text", "", "Regional formulation support", "</span>", "text"),
    # ---------------- product-lines.json ----------------
    ("product-lines", "eyebrow", '<span class="section-eyebrow">', "Product Lines", "</span>", "text"),
    ("product-lines", "title", '<h2 id="forms-title">', "Five Dosage Forms Under One Roof", "</h2>", "text"),
    ("product-lines", "lead", "<p>", "From capsules to gummies — choose a format that fits your brand, or let us recommend the right one for your formula and target market.", "</p>", "text"),
    ("product-lines", "items.0.name", "<h3>", "Capsules", "</h3>", "text"),
    ("product-lines", "items.0.desc", "<p>", "Two-piece and one-piece capsules for powders, granules and oil-based actives.", "</p>", "text"),
    ("product-lines", "items.1.name", "<h3>", "Tablets", "</h3>", "text"),
    ("product-lines", "items.1.desc", "<p>", "Coated, uncoated and effervescent tablets with flexible release profiles.", "</p>", "text"),
    ("product-lines", "items.2.name", "<h3>", "Powders", "</h3>", "text"),
    ("product-lines", "items.2.desc", "<p>", "Stick sachets, jars and tubs for protein, collagen and wellness blends.", "</p>", "text"),
    ("product-lines", "items.3.name", "<h3>", "Gummies", "</h3>", "text"),
    ("product-lines", "items.3.desc", "<p>", "Fruit-flavored gummies without gelatin (pectin-based) or with gelatin.", "</p>", "text"),
    ("product-lines", "items.4.name", "<h3>", "Softgels", "</h3>", "text"),
    ("product-lines", "items.4.desc", "<p>", "Lipid-soluble actives in stable, easy-to-swallow softgel formats.", "</p>", "text"),
    ("product-lines", "note", "", "Sample lines — replace with confirmed product ranges, photos and specifications before go-live.", "", "text"),
    # ---------------- services.json ----------------
    ("services", "eyebrow", '<span class="section-eyebrow">', "How We Work", "</span>", "text"),
    ("services", "title", '<h2 id="services-title">', "Three Ways to Partner", "</h2>", "text"),
    ("services", "lead", "<p>", "Whether you need ready-made formulas to resell or a full custom product built from scratch, we adapt the scope to your goals.", "</p>", "text"),
    ("services", "cards.0.title", "<h3>", "Wholesale", "</h3>", "text"),
    ("services", "cards.0.desc", "<p>", "Buy our existing catalog of proven formulations at wholesale terms for your distribution channels — the fastest route to market.", "</p>", "text"),
    ("services", "cards.0.link", ">", "Ask for the catalog", "", "text"),
    ("services", "cards.1.title", "<h3>", "OEM — Your Formula", "</h3>", "text"),
    ("services", "cards.1.desc", "<p>", "Bring your own formula and we manufacture, package and deliver it to your specification, with transparent QC at every step.", "</p>", "text"),
    ("services", "cards.1.link", ">", "See the process", "", "text"),
    ("services", "cards.2.title", "<h3>", "ODM — We Design It", "</h3>", "text"),
    ("services", "cards.2.desc", "<p>", "Share your positioning and target market; our development team creates the formula, flavor and packaging concept for you.", "</p>", "text"),
    ("services", "cards.2.link", ">", "Start a project", "", "text"),
    # ---------------- capabilities.json ----------------
    ("capabilities", "eyebrow", '<span class="section-eyebrow">', "Why Partners Choose Us (Sample)", "</span>", "text"),
    ("capabilities", "title", '<h2 id="cap-title">', "Built for Institutional Trust", "</h2>", "text"),
    ("capabilities", "lead", "<p>", "Sample capability dimensions — replace percentages, certification numbers and client references with verified evidence only.", "</p>", "text"),
    ("capabilities", "features.0.title", "<h4>", "Development Lab", "</h4>", "text"),
    ("capabilities", "features.0.desc", "<p>", "In-house formulation and stability testing to develop, scale and document your product.", "</p>", "text"),
    ("capabilities", "features.1.title", "<h4>", "Quality Control", "</h4>", "text"),
    ("capabilities", "features.1.desc", "<p>", "Raw material, in-process and finished-product checks against your agreed specification.", "</p>", "text"),
    ("capabilities", "features.2.title", "<h4>", "Regulatory &amp; Labeling", "</h4>", "text"),
    ("capabilities", "features.2.desc", "<p>", "Label text, claims and compliance review support for your target markets.", "</p>", "text"),
    ("capabilities", "features.3.title", "<h4>", "Export &amp; Logistics", "</h4>", "text"),
    ("capabilities", "features.3.desc", "<p>", "Packing, documentation and shipping coordination for each destination market.", "</p>", "text"),
    ("capabilities", "credentials.title", "<h4>", "Credentials — to be provided (Sample)", "</h4>", "text"),
    ("capabilities", "credentials.text_html",
     "<p>",
     "Facility certifications, audit reports, test records and client references are intentional placeholders in this demo. Confirm and publish only verified credentials: ",
     "<em>GMP / HACCP / ISO / FDA registration / EU compliance status — replace this list with your real certificates.</em></p>",
     "html"),  # tail keeps <em>…</em></p>
    # ---------------- markets.json ----------------
    ("markets", "eyebrow", '<span class="section-eyebrow" style="color:#c5cbd6">', "Target Markets", "</span>", "text"),
    ("markets", "title", '<h2 id="market-title">', "Where We Supply", "</h2>", "text"),
    ("markets", "lead", '<p style="color:#c5cbd6">', "Sample overview of the three target regions — confirm registrations, documents and timelines per country before claiming coverage.", "</p>", "text"),
    ("markets", "regions.0.name", '<h3 style="color:var(--text-inverse)"><span aria-hidden="true">🇪🇺</span> ', "Europe", "</h3>", "text"),
    ("markets", "regions.0.desc", '<p style="color:#9aa2ae">', "Wholesale and private-label programs supporting EU market entry requirements.", "</p>", "text"),
    ("markets", "regions.1.name", '<h3 style="color:var(--text-inverse)"><span aria-hidden="true">🇺🇸</span> ', "United States", "</h3>", "text"),
    ("markets", "regions.1.desc", '<p style="color:#9aa2ae">', "OEM and ODM programs with documentation support for US distribution.", "</p>", "text"),
    ("markets", "regions.2.name", '<h3 style="color:var(--text-inverse)"><span aria-hidden="true">🌏</span> ', "Southeast Asia", "</h3>", "text"),
    ("markets", "regions.2.desc", '<p style="color:#9aa2ae">', "Regional formulation, flavor and packaging support for emerging markets.", "</p>", "text"),
    ("markets", "note_compliance", "> ", "Sample compliance note", "", "text"),  # 3 bullets
    ("markets", "note_logistics", "> ", "Sample logistics note", "", "text"),  # 3 bullets
    # ---------------- about.json ----------------
    ("about", "eyebrow", '<span class="section-eyebrow">', "About Us", "</span>", "text"),
    ("about", "title", '<h2 id="about-title">', "A Manufacturing Partner, Not Just a Supplier", "</h2>", "text"),
    ("about", "lead", "<p>", "Sample company story. Replace with your real founding story, facility details and team background before publishing.", "</p>", "text"),
    ("about", "story_header", '<p style="max-width:var(--reading);font-size:17px;color:var(--text-muted);margin-bottom:48px">\n      ',
     "Zili Nutrition positions itself as a contract manufacturer for dietary supplements: private-label production, formula development and OEM support across three regions — Europe, the United States and Southeast Asia. This paragraph is placeholder copy that must be rewritten with the company's real history, mission and evidence.",
     "\n    </p>", "text"),
    ("about", "cells.0.title", "<h3>", "R&amp;D &amp; Formulation", "</h3>", "text"),
    ("about", "cells.0.desc", "<p>", "In-house development team covering new formulas, dosage-form selection, flavor masking and stability programs.", "</p>", "text"),
    ("about", "cells.1.title", "<h3>", "Production Capacity", "</h3>", "text"),
    ("about", "cells.1.desc", "<p>", "Blending, encapsulation, tableting and packaging lines with batch records and traceability. (Add real capacity figures.)", "</p>", "text"),
    ("about", "cells.2.title", "<h3>", "Quality Assurance", "</h3>", "text"),
    ("about", "cells.2.desc", "<p>", "Raw material release, in-process monitoring, finished goods testing and retained samples. (Add real lab info.)", "</p>", "text"),
    ("about", "cells.3.title", "<h3>", "Supply Chain", "</h3>", "text"),
    ("about", "cells.3.desc", "<p>", "Qualified raw material suppliers, transparent sourcing and export documentation support. (Add real supplier policy.)", "</p>", "text"),
    # ---------------- products.json ----------------
    ("products", "eyebrow", '<span class="section-eyebrow">', "Products", "</span>", "text"),
    ("products", "title", '<h2 id="products-title">', "Supplement Categories &amp; Formats", "</h2>", "text"),
    ("products", "lead", "<p>", "Sample category map only — final product matrix, specifications, photos and claims must be confirmed with the company before go-live.", "</p>", "text"),
    ("products", "categories.0.title", "<h3>", "Protein &amp; Sports", "</h3>", "text"),
    ("products", "categories.0.desc", "<p>", "Protein powders, BCAA/EAA, recovery blends and pre-workout formats.", "</p>", "text"),
    ("products", "categories.1.title", "<h3>", "Beauty &amp; Collagen", "</h3>", "text"),
    ("products", "categories.1.desc", "<p>", "Collagen peptides, hyaluronic acid, biotin and antioxidant blends.", "</p>", "text"),
    ("products", "categories.2.title", "<h3>", "Wellness Essentials", "</h3>", "text"),
    ("products", "categories.2.desc", "<p>", "Multivitamins, minerals, fish oil/omega and joint-support formulas.", "</p>", "text"),
    ("products", "categories.3.title", "<h3>", "Herbal &amp; Specialty", "</h3>", "text"),
    ("products", "categories.3.desc", "<p>", "Botanical extracts, digestive enzymes, probiotics and specialty actives.", "</p>", "text"),
    ("products", "boundary.title", "<h4>", "Product scope &amp; boundary", "</h4>", "text"),
    ("products", "boundary.p1_before", "<p>This site presents <strong>", "sample", "</strong> categories. Dietary supplements are not medicines: no therapeutic or disease-related claims are made here.</p>", "html"),
    ("products", "boundary.p2", "<p>", "All product claims, ingredient lists, dosage instructions and compliance statements shown in this demo must be reviewed by qualified regulatory staff and the company before external use.", "</p>", "text"),
    # ---------------- oem.json ----------------
    ("oem", "eyebrow", '<span class="section-eyebrow">', "OEM / ODM Services", "</span>", "text"),
    ("oem", "title", '<h2 id="oem-title">', "From Brief to Delivery, One Process", "</h2>", "text"),
    ("oem", "lead", "<p>", "Sample process flow. Actual timelines, deliverables and milestones to be confirmed per project.", "</p>", "text"),
    ("oem", "steps.0.title", "<h3>", "Inquiry &amp; Brief", "</h3>", "text"),
    ("oem", "steps.0.desc", "<p>", "Share your product idea, formula, goals and target market with our team.", "</p>", "text"),
    ("oem", "steps.1.title", "<h3>", "Feasibility &amp; Proposal", "</h3>", "text"),
    ("oem", "steps.1.desc", "<p>", "We assess raw materials, dosage form, cost and regulatory fit, then propose scope.", "</p>", "text"),
    ("oem", "steps.2.title", "<h3>", "Sample Development", "</h3>", "text"),
    ("oem", "steps.2.desc", "<p>", "Lab samples and prototypes are developed for your review and testing.", "</p>", "text"),
    ("oem", "steps.3.title", "<h3>", "Quote &amp; Agreement", "</h3>", "text"),
    ("oem", "steps.3.desc", "<p>", "Final pricing, MOQ, terms and documentation are agreed in writing.", "</p>", "text"),
    ("oem", "steps.4.title", "<h3>", "Production", "</h3>", "text"),
    ("oem", "steps.4.desc", "<p>", "Manufacturing runs to your approved specification with batch records.", "</p>", "text"),
    ("oem", "steps.5.title", "<h3>", "Quality Control", "</h3>", "text"),
    ("oem", "steps.5.desc", "<p>", "In-process and finished-product testing against the agreed spec.", "</p>", "text"),
    ("oem", "steps.6.title", "<h3>", "Packaging &amp; Labeling", "</h3>", "text"),
    ("oem", "steps.6.desc", "<p>", "Custom packaging, labels and language variants prepared for your market.", "</p>", "text"),
    ("oem", "steps.7.title", "<h3>", "Delivery &amp; Support", "</h3>", "text"),
    ("oem", "steps.7.desc", "<p>", "Export documentation, shipping and post-delivery support.", "</p>", "text"),
    ("oem", "cells.0.title", "<h3>", "What we can do (Sample)", "</h3>", "text"),
    ("oem", "cells.0.desc", "<p>", "Custom formulas, dosage-form selection, flavor/packaging design, label text drafting and export document support.", "</p>", "text"),
    ("oem", "cells.1.title", "<h3>", "What we don't do", "</h3>", "text"),
    ("oem", "cells.1.desc", "<p>", "This demo does not promise drug manufacturing, medical claims, or retail consumer sales. Add the real service boundary statement here.", "</p>", "text"),
    ("oem", "cells.2.title", "<h3>", "Sample boundaries", "</h3>", "text"),
    ("oem", "cells.2.desc", "<p>", "MOQ, lead time, capacity and certifications marked as placeholders — confirm with the company for accurate numbers.", "</p>", "text"),
    # ---------------- contact.json ----------------
    ("contact", "eyebrow", '<span class="section-eyebrow">', "Contact", "</span>", "text"),
    ("contact", "title", '<h2 id="contact-title">', "Request a Quote", "</h2>", "text"),
    ("contact", "lead", "<p>", "Tell us what you need and which market you sell into. A sample message flow — connect to your real inbox before going live.", "</p>", "text"),
    ("contact", "form.name_label", ">", "Full name", ' <span class="required" aria-hidden="true">*</span></label>', "html"),
    ("contact", "form.email_label", ">", "Business email", ' <span class="required" aria-hidden="true">*</span></label>', "html"),
    ("contact", "form.company_label", ">", "Company", ' <span class="required" aria-hidden="true">*</span></label>', "html"),
    ("contact", "form.market_label", ">", "Target market", ' <span class="required" aria-hidden="true">*</span></label>', "html"),
    ("contact", "form.market_placeholder", 'value="" selected disabled>', "Select a market…", "</option>", "text"),
    ("contact", "form.market_europe", 'value="europe">', "Europe", "</option>", "text"),
    ("contact", "form.market_us", 'value="us">', "United States", "</option>", "text"),
    ("contact", "form.market_seasia", 'value="seasia">', "Southeast Asia", "</option>", "text"),
    ("contact", "form.market_global", 'value="global">', "Global / Other", "</option>", "text"),
    ("contact", "form.message_label", ">", "How can we help?", ' <span class="required" aria-hidden="true">*</span></label>', "html"),
    ("contact", "form.message_placeholder", 'placeholder="', "Product idea, dosage form, estimated volume, timeline… (sample prompt)", '"', "text"),
    ("contact", "form.submit", ">", "Submit Inquiry", "</button>", "text"),
    ("contact", "form.privacy_note", '<p class="form-note">',
     "Privacy (Sample): by submitting, you agree that we may use your details to respond to this inquiry. Replace with your real privacy statement and data-processing terms before go-live.",
     "</p>", "text"),
    ("contact", "direct.title", "<h3>", "Direct contact", "</h3>", "text"),
    ("contact", "direct.email_label", "<strong>", "Email", "</strong>", "text"),
    ("contact", "direct.email_prefix", '<a href="mailto:', "zvitahealth@outlook.com", '">', "html"),
    ("contact", "direct.email_text", "", "zvitahealth@outlook.com", "</a></span></div>", "text"),
    ("contact", "direct.location_label", "<strong>", "Location", "</strong>", "text"),
    ("contact", "direct.location", "<span>", "Zhengzhou, Henan, China", "</span>", "text"),
    ("contact", "direct.response_label", "<strong>", "Response time", "</strong>", "text"),
    ("contact", "direct.response", "<span>", "Sample: within 1 business day", "</span>", "text"),
    ("contact", "direct.whatsapp_label", "<strong>", "WhatsApp", "</strong>", "text"),
    ("contact", "direct.whatsapp", "<span>", "+86 177 0069 9079", "</span>", "text"),
    ("contact", "direct.website_label", "<strong>", "Website", "</strong>", "text"),
    ("contact", "direct.website_url", '<a href="', "https://www.zvitahealth.com", '" rel="noopener">', "html"),
    ("contact", "direct.website_text", "", "www.zvitahealth.com", "</a></span></div>", "text"),
    ("contact", "note", '<p style="margin-top:24px;font-size:14px;color:var(--text-muted)">\n          ', "We serve business customers (wholesalers, brands, importers). We do not sell directly to consumers on this site.", "\n        </p>", "text"),
]

# ------------------------------------------------------------------ run ----
def assign(data, path, value):
    parts = path.split(".")
    node = data
    for p in parts[:-1]:
        node = node.setdefault(p, {})
    node[parts[-1]] = value


def main():
    if not SRC.exists():
        raise SystemExit(f"source not found: {SRC}")
    text = SRC.read_text(encoding="utf-8")
    data = defaultdict(dict)
    expanded = 0

    for file_name, path, before, editable, after, kind in PLAN:
        frag = before + editable + after
        count = text.count(frag)
        if count == 0:
            raise SystemExit(f"[{path}] fragment NOT FOUND:\n  {frag!r}")
        ph = ("{{" if kind == "text" else "{{{") + file_name + "." + path + ("}}" if kind == "text" else "}}}")
        replacement = before + ph + after
        text = text.replace(frag, replacement)
        # strip one redundant occurrence for html kinds where before/after kept the
        # real markup; for text kinds store the raw text node.
        value = html.unescape(editable) if kind == "text" else editable
        assign(data[file_name], path, value)
        expanded += count
        print(f"ok  {file_name}/{path}  x{count}  [{kind}]")

    TPL.parent.mkdir(parents=True, exist_ok=True)
    TPL.write_text(text, encoding="utf-8")
    print(f"\ntemplate written: {TPL} ({len(text)} bytes, {expanded} replacements)")

    # placeholder check: every {{...}} / {{{...}}} in the template is one we produced
    produced = set()
    for f, p, _, _, _, kind in PLAN:
        produced.add(("{{" if kind == "text" else "{{{") + f + "." + p + ("}}" if kind == "text" else "}}}"))
    found = set(re.findall(r"\{\{\{?[^}]*\}?\}\}", text))
    if not (found <= produced):
        raise SystemExit(f"unexpected placeholders: {sorted(found - produced)}")
    if len(found) != len(produced):
        raise SystemExit(f"placeholder mismatch: template has {len(found)}, expected {len(produced)}")

    OUT.mkdir(parents=True, exist_ok=True)
    for file_name, payload in sorted(data.items()):
        target = OUT / f"{file_name}.json"
        target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"content written: {target}")
    print("\ndone.")


if __name__ == "__main__":
    main()