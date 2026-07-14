#!/usr/bin/env python3
"""Generate proprietes.html + SEO detail pages from data/properties.json."""

from __future__ import annotations

import json
import re
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE_URL = "https://vendreavecsabrina.ca"
CENTRIS_AGENT_URL = (
    "https://www.centris.ca/fr/courtier-immobilier~sabrina-lagasse~proprio-direct/h3466"
)
PROPRIO_AGENT_URL = "https://propriodirect.com/sabrina-lagasse"


def load_registry() -> dict:
    return json.loads((ROOT / "data" / "properties.json").read_text(encoding="utf-8"))


def public_path(listing: dict) -> str:
    return listing.get("publicPath") or (
        f"/{listing['country']}/{listing['province']}/{listing['city']}/"
        f"{listing['sector']}/{listing['street']}/"
    )


def asset_prefix(depth: int) -> str:
    return "../" * depth if depth else ""


def _nav_link_class(active: str, key: str) -> str:
    if key == active:
        return "text-brand transition-colors"
    return "hover:text-brand transition-colors"


def site_chrome(active: str, depth: int = 0) -> tuple[str, str]:
    p = asset_prefix(depth)
    nav_cls = {
        "accueil": _nav_link_class(active, "accueil"),
        "proprietes": _nav_link_class(active, "proprietes"),
        "services": _nav_link_class(active, "services"),
        "blog": _nav_link_class(active, "blog"),
        "ressources": _nav_link_class(active, "ressources"),
        "apropos": _nav_link_class(active, "apropos"),
        "faq": _nav_link_class(active, "faq"),
    }
    mobile_cls = {
        k: (
            "mobile-link text-brand transition-colors transform translate-y-4 opacity-0 "
            "transition-all duration-300"
            if active == k
            else "mobile-link text-white hover:text-brand transition-colors transform "
            "translate-y-4 opacity-0 transition-all duration-300"
        )
        for k in nav_cls
    }
    delays = {
        "accueil": "delay-100",
        "proprietes": "delay-150",
        "services": "delay-200",
        "blog": "delay-250",
        "ressources": "delay-275",
        "apropos": "delay-300",
        "faq": "delay-325",
    }

    header = f"""<nav class="fixed w-full top-0 z-50 pt-6 px-4 md:px-8 transition-all duration-300">
        <div class="max-w-7xl mx-auto bg-white/10 backdrop-blur-xl border border-white/10 shadow-[0_8px_32px_0_rgba(0,0,0,0.3)] rounded-full px-6 py-4 flex justify-between items-center text-white relative z-50">
            <a href="{p}index.html" class="font-serif italic text-2xl font-semibold tracking-wide flex items-center gap-2 group">
                Sabrina Lagassé
            </a>
            <div class="hidden lg:flex space-x-8 text-sm font-medium tracking-wide">
                <a href="{p}index.html" class="{nav_cls['accueil']}">Accueil</a>
                <a href="{p}proprietes.html" class="{nav_cls['proprietes']}">Propriétés</a>
                <a href="{p}services.html" class="{nav_cls['services']}">Services</a>
                <a href="{p}blog.html" class="{nav_cls['blog']}">Blog</a>
                <a href="{p}ressources.html" class="{nav_cls['ressources']}">Ressources</a>
                <a href="{p}about.html" class="{nav_cls['apropos']}">À propos</a>
                <a href="{p}faq.html" class="{nav_cls['faq']}">FAQ</a>
            </div>
            <div class="flex items-center gap-4">
                <a href="tel:+15147963979" class="hidden sm:flex bg-white text-black px-6 py-2.5 rounded-full text-sm font-bold hover:bg-brand hover:text-white hover:scale-105 transition-all items-center gap-2">
                    <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" /></svg>
                    (514) 796-3979
                </a>
                <button id="mobile-menu-btn" class="lg:hidden p-1 text-white hover:text-brand focus:outline-none transition-colors" aria-label="Ouvrir le menu">
                    <svg id="icon-open" class="w-7 h-7" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" /></svg>
                    <svg id="icon-close" class="w-7 h-7 hidden" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
                </button>
            </div>
        </div>
        <div id="mobile-menu" class="fixed inset-0 bg-[#1e1e1e]/95 backdrop-blur-3xl z-40 opacity-0 pointer-events-none transition-all duration-500 flex flex-col justify-center items-center">
            <div class="flex flex-col items-center space-y-8 text-3xl font-serif italic">
                <a href="{p}index.html" class="{mobile_cls['accueil']} {delays['accueil']}">Accueil</a>
                <a href="{p}proprietes.html" class="{mobile_cls['proprietes']} {delays['proprietes']}">Propriétés</a>
                <a href="{p}services.html" class="{mobile_cls['services']} {delays['services']}">Services</a>
                <a href="{p}blog.html" class="{mobile_cls['blog']} {delays['blog']}">Blog</a>
                <a href="{p}ressources.html" class="{mobile_cls['ressources']} {delays['ressources']}">Ressources</a>
                <a href="{p}about.html" class="{mobile_cls['apropos']} {delays['apropos']}">À propos</a>
                <a href="{p}faq.html" class="{mobile_cls['faq']} {delays['faq']}">FAQ</a>
                <a href="tel:+15147963979" class="mobile-link mt-8 bg-brand text-white px-8 py-3 rounded-full text-lg font-sans font-bold not-italic hover:scale-105 transform translate-y-4 opacity-0 transition-all duration-300 delay-[400ms]">
                    Appeler le (514) 796-3979
                </a>
            </div>
        </div>
    </nav>"""

    footer = f"""<footer class="relative bg-[#1e1e1e] pt-20 pb-10 border-t border-white/10 overflow-hidden">
        <div class="absolute bottom-0 right-1/2 translate-x-1/2 translate-y-1/2 w-[800px] h-[300px] bg-brand/5 rounded-full blur-[120px] pointer-events-none"></div>
        <div class="relative z-10 max-w-7xl mx-auto px-6 md:px-8">
            <div class="grid grid-cols-1 md:grid-cols-12 gap-12 lg:gap-8 mb-16">
                <div class="md:col-span-5 lg:col-span-4 space-y-6">
                    <a href="{p}index.html" class="font-serif italic text-2xl font-semibold tracking-wide flex items-center gap-2 text-white group">
                        <span class="w-2 h-2 rounded-full bg-brand group-hover:scale-150 transition-transform duration-300"></span>
                        Sabrina Lagassé
                    </a>
                    <p class="text-gray-300 text-sm leading-relaxed pr-4">
                        Votre partenaire d'excellence pour l'achat, la vente et l'évaluation de propriétés. L'immobilier repensé avec une approche sur mesure, transparente et dévouée.
                    </p>
                    <div class="flex gap-4 pt-2">
                        <a href="#" aria-label="Instagram" class="w-10 h-10 rounded-full bg-white/5 border border-white/10 flex items-center justify-center text-white hover:bg-brand hover:border-brand hover:-translate-y-1 transition-all duration-300">
                            <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 100 12.324 6.162 6.162 0 000-12.324zM12 16a4 4 0 110-8 4 4 0 010 8zm6.406-11.845a1.44 1.44 0 100 2.881 1.44 1.44 0 000-2.88z"/></svg>
                        </a>
                        <a href="#" aria-label="LinkedIn" class="w-10 h-10 rounded-full bg-white/5 border border-white/10 flex items-center justify-center text-white hover:bg-brand hover:border-brand hover:-translate-y-1 transition-all duration-300">
                            <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M4.98 3.5c0 1.381-1.11 2.5-2.48 2.5s-2.48-1.119-2.48-2.5c0-1.38 1.11-2.5 2.48-2.5s2.48 1.12 2.48 2.5zm.02 4.5h-5v16h5v-16zm7.982 0h-4.968v16h4.969v-8.399c0-4.67 6.029-5.052 6.029 0v8.399h4.988v-10.131c0-7.88-8.922-7.593-11.018-3.714v-2.155z"/></svg>
                        </a>
                    </div>
                </div>
                <div class="md:col-span-3 lg:col-span-2 lg:col-start-7">
                    <h4 class="text-white font-bold uppercase tracking-wider text-xs mb-6">Menu</h4>
                    <ul class="space-y-4">
                        <li><a href="{p}index.html" class="text-gray-400 hover:text-brand text-sm transition-colors flex items-center gap-2"><span class="w-1 h-1 rounded-full bg-brand/50"></span> Accueil</a></li>
                        <li><a href="{p}proprietes.html" class="text-gray-400 hover:text-brand text-sm transition-colors flex items-center gap-2"><span class="w-1 h-1 rounded-full bg-brand/50"></span> Propriétés</a></li>
                        <li><a href="{p}services.html" class="text-gray-400 hover:text-brand text-sm transition-colors flex items-center gap-2"><span class="w-1 h-1 rounded-full bg-brand/50"></span> Services</a></li>
                        <li><a href="{p}blog.html" class="text-gray-400 hover:text-brand text-sm transition-colors flex items-center gap-2"><span class="w-1 h-1 rounded-full bg-brand/50"></span> Blog</a></li>
                        <li><a href="{p}ressources.html" class="text-gray-400 hover:text-brand text-sm transition-colors flex items-center gap-2"><span class="w-1 h-1 rounded-full bg-brand/50"></span> Ressources</a></li>
                        <li><a href="{p}about.html" class="text-gray-400 hover:text-brand text-sm transition-colors flex items-center gap-2"><span class="w-1 h-1 rounded-full bg-brand/50"></span> À propos</a></li>
                        <li><a href="{p}faq.html" class="text-gray-400 hover:text-brand text-sm transition-colors flex items-center gap-2"><span class="w-1 h-1 rounded-full bg-brand/50"></span> FAQ</a></li>
                        <li><a href="{p}contact.html" class="text-gray-400 hover:text-brand text-sm transition-colors flex items-center gap-2"><span class="w-1 h-1 rounded-full bg-brand/50"></span> Contact</a></li>
                    </ul>
                </div>
                <div class="md:col-span-4 lg:col-span-3">
                    <h4 class="text-white font-bold uppercase tracking-wider text-xs mb-6">Coordonnées</h4>
                    <ul class="space-y-4 text-sm text-gray-400">
                        <li class="flex items-center gap-3">
                            <svg class="w-5 h-5 text-brand shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" /></svg>
                            <a href="tel:+15147963979" class="hover:text-brand transition-colors">(514) 796-3979</a>
                        </li>
                        <li class="flex items-center gap-3">
                            <svg class="w-5 h-5 text-brand shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" /></svg>
                            <a href="mailto:sabrina.lagasse@hotmail.com" class="hover:text-brand transition-colors">sabrina.lagasse@hotmail.com</a>
                        </li>
                    </ul>
                </div>
            </div>
            <div class="pt-8 border-t border-white/10 flex flex-col md:flex-row justify-between items-center gap-4 text-xs text-gray-500 font-medium tracking-wide">
                <p>&copy; 2026 Sabrina Lagassé. Tous droits réservés.</p>
                <div class="flex gap-6">
                    <a href="{p}politique-confidentialite.html" class="hover:text-brand transition-colors">Politique de confidentialité</a>
                    <span>Conception web par <a href="https://roymarketing.ca" target="_blank" rel="noopener noreferrer" class="text-brand hover:underline">Roy Marketing</a></span>
                </div>
            </div>
        </div>
    </footer>
    <script>
        document.addEventListener('DOMContentLoaded', () => {{
            const btn = document.getElementById('mobile-menu-btn');
            const menu = document.getElementById('mobile-menu');
            const iconOpen = document.getElementById('icon-open');
            const iconClose = document.getElementById('icon-close');
            const mobileLinks = document.querySelectorAll('.mobile-link');
            let isMenuOpen = false;

            function toggleMenu() {{
                isMenuOpen = !isMenuOpen;
                if (isMenuOpen) {{
                    menu.classList.remove('opacity-0', 'pointer-events-none');
                    menu.classList.add('opacity-100', 'pointer-events-auto');
                    setTimeout(() => {{
                        mobileLinks.forEach(link => {{
                            link.classList.remove('translate-y-4', 'opacity-0');
                            link.classList.add('translate-y-0', 'opacity-100');
                        }});
                    }}, 50);
                }} else {{
                    menu.classList.remove('opacity-100', 'pointer-events-auto');
                    menu.classList.add('opacity-0', 'pointer-events-none');
                    mobileLinks.forEach(link => {{
                        link.classList.remove('translate-y-0', 'opacity-100');
                        link.classList.add('translate-y-4', 'opacity-0');
                    }});
                }}
                iconOpen.classList.toggle('hidden');
                iconClose.classList.toggle('hidden');
                document.body.style.overflow = isMenuOpen ? 'hidden' : '';
            }}

            btn.addEventListener('click', toggleMenu);
            mobileLinks.forEach(link => {{
                link.addEventListener('click', () => {{
                    if (isMenuOpen) toggleMenu();
                }});
            }});
        }});
    </script>
    <div id="cookie-consent-banner" style="display:none" class="fixed bottom-0 left-0 right-0 z-[100] p-4 md:p-6 bg-[#1e1e1e] border-t border-white/20 shadow-[0_-8px_32px_rgba(0,0,0,0.4)] transition-all duration-300" role="dialog" aria-label="Consentement aux cookies">
        <div class="max-w-7xl mx-auto flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <p class="text-gray-300 text-sm md:text-base">
                Nous utilisons des cookies pour le bon fonctionnement du site et pour mémoriser vos préférences. Vous pouvez accepter ou refuser. <a href="{p}politique-confidentialite.html" class="text-brand hover:underline">Politique de confidentialité</a>.
            </p>
            <div class="flex gap-3 shrink-0">
                <button id="cookie-consent-refuse" type="button" class="px-5 py-2.5 rounded-full text-sm font-bold border border-white/20 text-white hover:border-brand hover:text-brand transition-colors">Refuser</button>
                <button id="cookie-consent-accept" type="button" class="px-5 py-2.5 rounded-full text-sm font-bold bg-brand text-white hover:bg-white hover:text-black transition-colors">Accepter</button>
            </div>
        </div>
    </div>
    <script src="{p}js/cookie-consent.js"></script>
    <a href="https://m.me/100057685980389" target="_blank" rel="noopener noreferrer" class="fixed bottom-6 right-6 z-50 w-14 h-14 md:w-16 md:h-16 rounded-full bg-[#d0103a] text-white flex items-center justify-center shadow-[0_4px_20px_rgba(208,16,58,0.5)] hover:scale-110 hover:shadow-[0_6px_28px_rgba(208,16,58,0.6)] transition-all duration-300" aria-label="Ouvrir une conversation sur Messenger">
        <svg class="w-7 h-7 md:w-8 md:h-8" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2C6.36 2 2 6.13 2 11.33c0 3.45 1.76 6.5 4.43 8.22-.22.8-.81 2.9-.93 3.35-.14.54.2.53.41.39.17-.11 2.69-1.81 3.79-2.58.64.09 1.3.14 2 .14 5.64 0 10-4.13 10-9.33S17.64 2 12 2zm-1.17 6.21l-2.92 3.45 3.46-1.95 1.46 1.46 2.92-3.45-3.46 1.95-1.46-1.46z"/></svg>
    </a>"""

    return header, footer


def head_block(
    *,
    title: str,
    description: str,
    canonical: str,
    og_image: str,
    depth: int = 0,
    extra: str = "",
) -> str:
    p = asset_prefix(depth)
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta content="width=device-width, initial-scale=1.0" name="viewport">
  <title>{escape(title)}</title>
  <meta name="description" content="{escape(description)}">
  <link rel="icon" type="image/svg+xml" href="{p}favicon.svg">
  <link rel="preconnect" href="https://fonts.gstatic.com">
  <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=DM+Sans:400,500,600,700,800,900|Playfair+Display:400,500,600,700,800,900&amp;subset=latin">
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {{
      theme: {{
        extend: {{
          fontFamily: {{
            sans: ['"DM Sans"', 'sans-serif'],
            serif: ['"Playfair Display"', 'serif'],
          }},
          colors: {{
            brand: '#d0103a',
          }}
        }}
      }}
    }}
  </script>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
  <link href="{p}assets/css/properties.css" rel="stylesheet">
  <link rel="canonical" href="{escape(canonical)}">
  <meta property="og:title" content="{escape(title)}">
  <meta property="og:description" content="{escape(description)}">
  <meta property="og:image" content="{escape(og_image)}">
  <meta property="og:image:secure_url" content="{escape(og_image)}">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:type" content="image/jpeg">
  <meta property="og:image:alt" content="{escape(title)}">
  <meta property="og:url" content="{escape(canonical)}">
  <meta property="og:type" content="website">
  <meta property="og:locale" content="fr_CA">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{escape(title)}">
  <meta name="twitter:description" content="{escape(description)}">
  <meta name="twitter:image" content="{escape(og_image)}">
  <meta name="twitter:image:alt" content="{escape(title)}">
{extra}
</head>"""


def listing_card_html(listing: dict, depth: int = 0) -> str:
    p = asset_prefix(depth)
    href = public_path(listing)
    img = f"{p}assets/img/proprietes/{listing['fallbackImage']}"
    badge = ""
    if listing.get("sold"):
        badge = '<span class="prop-badge sold">Vendu</span>'
    elif listing.get("isNew"):
        badge = '<span class="prop-badge new">Nouveauté</span>'

    meta_bits = []
    if listing.get("beds"):
        meta_bits.append(
            f'<span><i class="bi bi-door-closed"></i> {escape(str(listing["beds"]))} ch.</span>'
        )
    if listing.get("baths"):
        meta_bits.append(
            f'<span><i class="bi bi-droplet"></i> {escape(str(listing["baths"]))} sdb</span>'
        )
    size_value = listing.get("livingArea") or listing.get("size")
    if size_value:
        meta_bits.append(
            f'<span><i class="bi bi-bounding-box"></i> {escape(str(size_value))}</span>'
        )

    is_sold = bool(listing.get("sold"))
    price_html = (
        '<p class="prop-price prop-sold-label">Vendu</p>'
        if is_sold
        else f'<p class="prop-price">{escape(listing.get("price") or "")}</p>'
    )

    return f"""
        <article class="prop-card{" prop-card-sold" if is_sold else ""}">
          <a href="{escape(href)}" class="prop-card-media">
            <img src="{escape(img)}" alt="{escape(listing.get('title') or listing.get('address') or '')}" loading="lazy">
            {badge}
          </a>
          <div class="prop-card-body">
            <span class="prop-subtitle mb-1">{escape(listing.get('propertyType') or 'Propriété')}</span>
            {price_html}
            <h3 class="prop-address">{escape(listing.get('address') or '')}</h3>
            <p class="prop-city">{escape(listing.get('cityLabel') or '')}</p>
            <div class="prop-meta">{''.join(meta_bits)}</div>
            <a href="{escape(href)}" class="prop-cta">Voir la fiche <i class="bi bi-arrow-right ms-1"></i></a>
          </div>
        </article>"""


def generate_listings_page(registry: dict) -> None:
    header, footer = site_chrome("proprietes", depth=0)
    listings = registry.get("listings", [])
    active = [x for x in listings if not x.get("sold")]
    sold = [x for x in listings if x.get("sold")]
    ordered = active + sold

    cards = "\n".join(listing_card_html(item, depth=0) for item in ordered) or (
        '<p class="col-span-full text-center text-gray-400">Aucune propriété à afficher pour le moment.</p>'
    )

    description = (
        "Découvrez les propriétés en vigueur de Sabrina Lagassé, courtière immobilière "
        "Proprio Direct."
    )
    og_image = f"{BASE_URL}/social.png"
    if ordered:
        og_image = (
            f"{BASE_URL}/assets/img/proprietes/{ordered[0]['uls']}/og-share.jpg"
        )

    html = f"""{head_block(
        title="Propriétés - Sabrina Lagassé, courtière immobilière",
        description=description,
        canonical=f"{BASE_URL}/proprietes.html",
        og_image=og_image,
        depth=0,
    )}
<body class="antialiased bg-[#1e1e1e] text-white font-sans proprietes-page">
{header}
<main>
  <section class="properties-title-section">
    <div class="max-w-7xl mx-auto px-6 md:px-8 text-center">
      <div class="section-title-wrapper">
        <h1 class="title-with-lines font-serif">Propriétés</h1>
        <p class="text-gray-300">Découvrez mes inscriptions actuelles et mes propriétés vendues.</p>
      </div>
    </div>
  </section>
  <section class="section properties-grid pt-0 pb-24">
    <div class="max-w-7xl mx-auto px-6 md:px-8">
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 md:gap-8">
{cards}
      </div>
      <div class="text-center properties-external-link">
        <a href="{PROPRIO_AGENT_URL}" target="_blank" rel="noopener" class="btn-outline">
          Voir aussi sur Proprio Direct
        </a>
      </div>
    </div>
  </section>
</main>
{footer}
</body>
</html>
"""
    (ROOT / "proprietes.html").write_text(html, encoding="utf-8")
    print("wrote proprietes.html")


def kv_list_html(data: dict | None, empty_message: str = "") -> str:
    if not data:
        return (
            f'<p class="text-gray-400 mb-0">{escape(empty_message)}</p>'
            if empty_message
            else ""
        )
    rows = [
        f"<li><strong>{escape(str(key))}</strong><span>{escape(str(value))}</span></li>"
        for key, value in data.items()
    ]
    return f'<ul class="property-facts">{"".join(rows)}</ul>'


def rooms_table_html(rooms: list | None) -> str:
    if not rooms:
        return ""
    rows = []
    for room in rooms:
        rows.append(
            "<tr>"
            f"<td>{escape(str(room.get('name') or ''))}</td>"
            f"<td>{escape(str(room.get('level') or ''))}</td>"
            f"<td>{escape(str(room.get('dimensions') or ''))}</td>"
            f"<td>{escape(str(room.get('flooring') or ''))}</td>"
            "</tr>"
        )
    return (
        '<div class="property-rooms-table">'
        "<table>"
        "<thead><tr><th>Pièce</th><th>Étage</th><th>Dimensions</th><th>Plancher</th></tr></thead>"
        f"<tbody>{''.join(rows)}</tbody>"
        "</table></div>"
    )


def generate_detail_page(listing: dict) -> None:
    depth = 5  # /ca/qc/city/sector/street/index.html
    header, footer = site_chrome("proprietes", depth=depth)
    p = asset_prefix(depth)
    path = public_path(listing)
    canonical = BASE_URL + path
    og_image = f"{BASE_URL}/assets/img/proprietes/{listing['uls']}/og-share.jpg"
    fallback = f"{p}assets/img/proprietes/{listing['fallbackImage']}"
    description = listing.get("description") or listing.get("shareTitle") or listing.get("title")
    if len(description) > 300:
        description = description[:297].rstrip() + "…"

    badge = ""
    if listing.get("sold"):
        badge = '<span class="prop-badge sold">Vendu</span>'
    elif listing.get("isNew"):
        badge = '<span class="prop-badge new">Nouveauté</span>'

    meta_rows = []
    if listing.get("beds"):
        meta_rows.append(
            f"<li><strong>Chambres</strong><span>{escape(str(listing['beds']))}</span></li>"
        )
    if listing.get("baths"):
        meta_rows.append(
            f"<li><strong>Salles de bain</strong><span>{escape(str(listing['baths']))}</span></li>"
        )
    size_value = listing.get("livingArea") or listing.get("size")
    if size_value:
        meta_rows.append(
            f"<li><strong>Superficie</strong><span>{escape(str(size_value))}</span></li>"
        )
    if listing.get("yearBuilt"):
        meta_rows.append(
            f"<li><strong>Année</strong><span>{escape(str(listing['yearBuilt']))}</span></li>"
        )
    if listing.get("floorLevel"):
        meta_rows.append(
            f"<li><strong>Niveau</strong><span>{escape(str(listing['floorLevel']))}</span></li>"
        )
    if listing.get("condoFees"):
        meta_rows.append(
            f"<li><strong>Frais de condo</strong><span>{escape(str(listing['condoFees']))}</span></li>"
        )
    if listing.get("parking"):
        meta_rows.append(
            f"<li><strong>Stationnement</strong><span>{escape(str(listing['parking']))}</span></li>"
        )
    if listing.get("postalCode"):
        meta_rows.append(
            f"<li><strong>Code postal</strong><span>{escape(str(listing['postalCode']))}</span></li>"
        )
    meta_rows.append(
        f"<li><strong>Inscription</strong><span>{escape(str(listing['uls']))}</span></li>"
    )

    city_label = listing["city"].replace("-", " ").title()
    sector_label = listing["sector"].replace("-", " ").title()
    city_line = escape(listing.get("cityLabel") or "")
    if listing.get("postalCode"):
        city_line += f" · {escape(str(listing['postalCode']))}"

    is_sold = bool(listing.get("sold"))
    price_html = (
        '<p class="prop-price prop-sold-label">Vendu</p>'
        if is_sold
        else f'<p class="prop-price">{escape(listing.get("price") or "")}</p>'
    )
    actions_html = ""
    if is_sold:
        actions_html = f"""
            <div class="property-actions">
              <a class="btn-outline" href="{escape(listing.get('proprioUrl') or '#')}" target="_blank" rel="noopener">Voir sur Proprio Direct</a>
              <a class="btn-outline" href="{escape(listing.get('centrisUrl') or '#')}" target="_blank" rel="noopener">Voir sur Centris</a>
            </div>"""
    else:
        actions_html = f"""
            <div class="property-actions">
              <a class="btn-primary" href="{p}contact.html">Demander une visite</a>
              <a class="btn-outline" href="{escape(listing.get('proprioUrl') or '#')}" target="_blank" rel="noopener">Voir sur Proprio Direct</a>
              <a class="btn-outline" href="{escape(listing.get('centrisUrl') or '#')}" target="_blank" rel="noopener">Voir sur Centris</a>
            </div>"""

    highlights_html = ""
    if listing.get("highlights"):
        highlights_html = f"""
          <div class="property-panel">
            <span class="prop-subtitle">Aperçu</span>
            <h2>Points saillants</h2>
            {kv_list_html(listing.get("highlights"))}
          </div>"""

    details_html = ""
    if listing.get("details"):
        details_html = f"""
          <div class="property-panel">
            <span class="prop-subtitle">Caractéristiques</span>
            <h2>Détails de la propriété</h2>
            {kv_list_html(listing.get("details"))}
          </div>"""

    inclusions_html = ""
    if listing.get("inclusions"):
        inclusions_html = f"""
          <div class="property-panel">
            <span class="prop-subtitle">Ce qui est inclus</span>
            <h2>Inclusions</h2>
            <p>{escape(listing.get("inclusions") or "")}</p>
          </div>"""

    exclusions_html = ""
    if listing.get("exclusions"):
        exclusions_html = f"""
          <div class="property-panel">
            <span class="prop-subtitle">Non inclus</span>
            <h2>Exclusions</h2>
            <p>{escape(listing.get("exclusions") or "")}</p>
          </div>"""

    rooms_html = ""
    rooms_table = rooms_table_html(listing.get("rooms"))
    if rooms_table:
        rooms_html = f"""
          <div class="property-panel">
            <span class="prop-subtitle">Aménagement</span>
            <h2>Pièces</h2>
            {rooms_table}
          </div>"""

    taxes_html = ""
    if listing.get("taxes"):
        taxes_html = f"""
          <div class="property-panel">
            <span class="prop-subtitle">Finances</span>
            <h2>Taxes et évaluation</h2>
            {kv_list_html(listing.get("taxes"))}
          </div>"""

    additional_html = ""
    if listing.get("additionalInfo"):
        additional_html = f"""
          <div class="property-panel property-panel-muted">
            <span class="prop-subtitle">À noter</span>
            <h2>Information supplémentaire</h2>
            <p>{escape(listing.get("additionalInfo") or "")}</p>
          </div>"""

    body = f"""{head_block(
        title=listing.get("shareTitle") or listing.get("title") or "Propriété",
        description=description,
        canonical=canonical,
        og_image=og_image,
        depth=depth,
    )}
<body class="antialiased bg-[#1e1e1e] text-white font-sans property-details-page">
{header}
<main>
  <section class="section property-detail">
    <div class="max-w-7xl mx-auto px-6 md:px-8">
      <nav class="prop-breadcrumb" aria-label="Fil d'Ariane">
        <a href="{p}proprietes.html">Propriétés</a>
        <span>/</span>
        <span>{escape(city_label)}</span>
        <span>/</span>
        <span>{escape(sector_label)}</span>
      </nav>

      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 lg:gap-8 items-start">
        <div class="lg:col-span-7">
          <section class="property-media"
            data-uls="{escape(listing['uls'])}"
            data-share-title="{escape(listing.get('shareTitle') or '')}"
            data-share-url="{escape(canonical)}"
            data-share-image="{escape(og_image)}"
            data-fallback-image="{escape(fallback)}"
            data-assets-base="{p}assets/img/proprietes/">
            <div class="property-gallery">
              <div class="gallery-main-wrap">
                <img id="property-gallery-main" src="{escape(fallback)}" alt="{escape(listing.get('title') or '')}">
                <button type="button" id="property-gallery-prev" aria-label="Photo précédente"><i class="bi bi-chevron-left"></i></button>
                <button type="button" id="property-gallery-next" aria-label="Photo suivante"><i class="bi bi-chevron-right"></i></button>
                <span id="property-gallery-counter">1 / 1</span>
                {badge}
              </div>
              <div id="property-gallery-thumbs" class="gallery-thumbs"></div>
            </div>
            <div class="property-share">
              <p>Partager cette propriété</p>
              <div id="property-share-buttons"></div>
            </div>
          </section>
        </div>
        <div class="lg:col-span-5">
          <div class="property-summary">
            <span class="prop-subtitle">{escape(listing.get('propertyType') or 'Propriété')}</span>
            {price_html}
            <h1>{escape(listing.get('address') or listing.get('title') or '')}</h1>
            <p class="prop-city">{city_line}</p>
            <ul class="property-facts">
              {''.join(meta_rows)}
            </ul>
            {actions_html}
          </div>
        </div>
      </div>

      <div class="mt-8 max-w-4xl">
          <div class="property-description">
            <span class="prop-subtitle">À propos</span>
            <h2>Description de la propriété</h2>
            <p>{escape(listing.get('description') or 'Description à venir.')}</p>
          </div>
          {highlights_html}
          {details_html}
          {inclusions_html}
          {exclusions_html}
          {rooms_html}
          {taxes_html}
          {additional_html}
      </div>
    </div>
  </section>
</main>
{footer}
<script src="{p}assets/js/property-gallery.js" defer></script>
<script src="{p}assets/js/property-share.js" defer></script>
</body>
</html>
"""

    dest_dir = (
        ROOT
        / listing["country"]
        / listing["province"]
        / listing["city"]
        / listing["sector"]
        / listing["street"]
    )
    dest_dir.mkdir(parents=True, exist_ok=True)
    (dest_dir / "index.html").write_text(body, encoding="utf-8")
    print(f"wrote {dest_dir.relative_to(ROOT) / 'index.html'}")


def prune_stale_detail_pages(registry: dict) -> None:
    active_paths = {
        (
            listing["country"],
            listing["province"],
            listing["city"],
            listing["sector"],
            listing["street"],
        )
        for listing in registry.get("listings", [])
    }
    ca_root = ROOT / "ca" / "qc"
    if not ca_root.exists():
        return
    for index in ca_root.rglob("index.html"):
        rel = index.relative_to(ROOT)
        parts = rel.parts
        if len(parts) != 6:
            continue
        key = parts[:5]
        if key not in active_paths:
            index.unlink()
            # clean empty parents
            parent = index.parent
            for _ in range(5):
                if parent.exists() and not any(parent.iterdir()):
                    parent.rmdir()
                    parent = parent.parent
                else:
                    break
            print(f"removed stale {rel}")


def update_nav_links() -> None:
    """Point nav/footer 'Propriétés' Centris links to the local listings page."""
    pattern = re.compile(
        r'<a href="'
        + re.escape(CENTRIS_AGENT_URL)
        + r'"(?:\s+target="_blank")?(?:\s+rel="noopener noreferrer")?',
        re.IGNORECASE,
    )
    for path in ROOT.glob("*.html"):
        if path.name == "proprietes.html":
            continue
        text = path.read_text(encoding="utf-8")
        updated = pattern.sub('<a href="proprietes.html"', text)
        if updated != text:
            path.write_text(updated, encoding="utf-8")
            print(f"updated Propriétés links in {path.name}")


def generate_all() -> None:
    registry = load_registry()
    generate_listings_page(registry)
    for listing in registry.get("listings", []):
        generate_detail_page(listing)
    prune_stale_detail_pages(registry)
    update_nav_links()


if __name__ == "__main__":
    generate_all()
