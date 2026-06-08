from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate
import datetime

# ─── COULEURS ────────────────────────────────────────────────────────────────
NAVY       = colors.HexColor("#0f172a")
PURPLE     = colors.HexColor("#7c3aed")
PURPLE_LT  = colors.HexColor("#a78bfa")
PURPLE_BG  = colors.HexColor("#ede9fe")
GOLD       = colors.HexColor("#f59e0b")
GOLD_BG    = colors.HexColor("#fef3c7")
GREEN      = colors.HexColor("#10b981")
GREEN_BG   = colors.HexColor("#d1fae5")
BLUE       = colors.HexColor("#3b82f6")
BLUE_BG    = colors.HexColor("#dbeafe")
RED        = colors.HexColor("#ef4444")
GRAY_DARK  = colors.HexColor("#1e293b")
GRAY_MID   = colors.HexColor("#475569")
GRAY_LIGHT = colors.HexColor("#f1f5f9")
GRAY_BORDER= colors.HexColor("#e2e8f0")
WHITE      = colors.white
BLACK      = colors.HexColor("#0f172a")

W, H = A4

# ─── STYLES ──────────────────────────────────────────────────────────────────
def make_styles():
    return {
        "cover_title": ParagraphStyle("cover_title",
            fontName="Helvetica-Bold", fontSize=42, textColor=WHITE,
            leading=50, alignment=TA_CENTER, spaceAfter=6),
        "cover_sub": ParagraphStyle("cover_sub",
            fontName="Helvetica", fontSize=14, textColor=colors.HexColor("#c4b5fd"),
            leading=20, alignment=TA_CENTER, spaceAfter=4),
        "cover_meta": ParagraphStyle("cover_meta",
            fontName="Helvetica", fontSize=10, textColor=colors.HexColor("#94a3b8"),
            alignment=TA_CENTER, spaceAfter=2),
        "h1": ParagraphStyle("h1",
            fontName="Helvetica-Bold", fontSize=20, textColor=PURPLE,
            leading=26, spaceBefore=20, spaceAfter=8,
            borderPad=0),
        "h2": ParagraphStyle("h2",
            fontName="Helvetica-Bold", fontSize=14, textColor=NAVY,
            leading=18, spaceBefore=14, spaceAfter=6),
        "h3": ParagraphStyle("h3",
            fontName="Helvetica-Bold", fontSize=11, textColor=GRAY_DARK,
            leading=14, spaceBefore=10, spaceAfter=4),
        "body": ParagraphStyle("body",
            fontName="Helvetica", fontSize=10, textColor=GRAY_MID,
            leading=16, spaceAfter=6, alignment=TA_JUSTIFY),
        "body_bold": ParagraphStyle("body_bold",
            fontName="Helvetica-Bold", fontSize=10, textColor=GRAY_DARK,
            leading=14, spaceAfter=4),
        "bullet": ParagraphStyle("bullet",
            fontName="Helvetica", fontSize=10, textColor=GRAY_MID,
            leading=16, spaceAfter=3, leftIndent=16,
            bulletIndent=4),
        "caption": ParagraphStyle("caption",
            fontName="Helvetica-Oblique", fontSize=8.5, textColor=GRAY_MID,
            alignment=TA_CENTER, spaceAfter=4),
        "tag": ParagraphStyle("tag",
            fontName="Helvetica-Bold", fontSize=8, textColor=PURPLE,
            leading=10, alignment=TA_CENTER),
        "footer": ParagraphStyle("footer",
            fontName="Helvetica", fontSize=8, textColor=GRAY_MID,
            alignment=TA_CENTER),
        "toc_title": ParagraphStyle("toc_title",
            fontName="Helvetica-Bold", fontSize=11, textColor=NAVY, leading=16),
        "toc_item": ParagraphStyle("toc_item",
            fontName="Helvetica", fontSize=10, textColor=GRAY_MID,
            leading=18, leftIndent=10),
        "toc_sub": ParagraphStyle("toc_sub",
            fontName="Helvetica", fontSize=9, textColor=GRAY_MID,
            leading=15, leftIndent=24),
        "note_title": ParagraphStyle("note_title",
            fontName="Helvetica-Bold", fontSize=9.5, textColor=PURPLE,
            leading=13),
        "note_body": ParagraphStyle("note_body",
            fontName="Helvetica", fontSize=9, textColor=GRAY_MID,
            leading=14),
        "code": ParagraphStyle("code",
            fontName="Courier", fontSize=8.5, textColor=colors.HexColor("#1e293b"),
            leading=13, leftIndent=10),
        "section_num": ParagraphStyle("section_num",
            fontName="Helvetica-Bold", fontSize=9, textColor=PURPLE_LT,
            leading=11, spaceAfter=2),
    }

S = make_styles()

# ─── PAGE CALLBACKS ──────────────────────────────────────────────────────────
def cover_background(canv, doc):
    canv.saveState()
    # Full dark background
    canv.setFillColor(NAVY)
    canv.rect(0, 0, W, H, fill=1, stroke=0)
    # Purple gradient band top
    canv.setFillColor(colors.HexColor("#3b0764"))
    canv.rect(0, H - 280, W, 280, fill=1, stroke=0)
    # Purple accent band
    canv.setFillColor(PURPLE)
    canv.rect(0, H - 6, W, 6, fill=1, stroke=0)
    # Gold bottom accent
    canv.setFillColor(GOLD)
    canv.rect(0, 0, W, 4, fill=1, stroke=0)
    # Decorative circles
    canv.setFillColor(colors.HexColor("#4c1d95"))
    canv.circle(W - 60, H - 60, 120, fill=1, stroke=0)
    canv.setFillColor(colors.HexColor("#2e1065"))
    canv.circle(60, H - 200, 80, fill=1, stroke=0)
    canv.setFillColor(colors.HexColor("#1e1b4b"))
    canv.circle(W//2, 80, 200, fill=1, stroke=0)
    # Gold dot
    canv.setFillColor(GOLD)
    canv.circle(W//2 + 90, H - 175, 8, fill=1, stroke=0)
    canv.restoreState()

def normal_page(canv, doc):
    canv.saveState()
    canv.setFillColor(WHITE)
    canv.rect(0, 0, W, H, fill=1, stroke=0)
    # Left purple bar
    canv.setFillColor(PURPLE)
    canv.rect(0, 0, 4, H, fill=1, stroke=0)
    # Top bar
    canv.setFillColor(GRAY_LIGHT)
    canv.rect(0, H - 38, W, 38, fill=1, stroke=0)
    canv.setFillColor(NAVY)
    canv.setFont("Helvetica-Bold", 9)
    canv.drawString(20, H - 22, "DUNIA PLATFORM")
    canv.setFillColor(GRAY_MID)
    canv.setFont("Helvetica", 8)
    canv.drawRightString(W - 20, H - 22, "Rapport Technique — 2025")
    # Bottom bar
    canv.setFillColor(GRAY_LIGHT)
    canv.rect(0, 0, W, 28, fill=1, stroke=0)
    canv.setFillColor(PURPLE)
    canv.rect(0, 0, 4, 28, fill=1, stroke=0)
    canv.setFillColor(GRAY_MID)
    canv.setFont("Helvetica", 8)
    canv.drawString(20, 10, "© 2025 Dunia Platform · Kinshasa, RDC")
    canv.setFillColor(PURPLE)
    canv.setFont("Helvetica-Bold", 9)
    canv.drawRightString(W - 20, 10, f"Page {doc.page - 1}")
    canv.restoreState()

# ─── HELPERS ─────────────────────────────────────────────────────────────────
def hr(color=GRAY_BORDER, thickness=0.5):
    return HRFlowable(width="100%", thickness=thickness, color=color, spaceAfter=6, spaceBefore=4)

def purple_hr():
    return HRFlowable(width="100%", thickness=1.5, color=PURPLE, spaceAfter=8, spaceBefore=4)

def section_header(num, title):
    return [
        Paragraph(f"SECTION {num}", S["section_num"]),
        Paragraph(title, S["h1"]),
        purple_hr(),
    ]

def info_box(title, lines, color=PURPLE, bg=PURPLE_BG):
    content = f'<font color="#{color.hexval()[1:]}" size="9"><b>{title}</b></font><br/>'
    for line in lines:
        content += f'<font size="9" color="#475569">• {line}</font><br/>'
    style = ParagraphStyle("box", fontName="Helvetica", fontSize=9,
        leading=14, spaceAfter=0)
    p = Paragraph(content, style)
    t = Table([[p]], colWidths=[W - 80*mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), bg),
        ("LEFTPADDING", (0,0), (-1,-1), 12),
        ("RIGHTPADDING", (0,0), (-1,-1), 12),
        ("TOPPADDING", (0,0), (-1,-1), 10),
        ("BOTTOMPADDING", (0,0), (-1,-1), 10),
        ("ROUNDEDCORNERS", (0,0), (-1,-1), [6,6,6,6]),
        ("BOX", (0,0), (-1,-1), 1, color),
    ]))
    return t

def feature_table(data, col_widths=None):
    if col_widths is None:
        col_widths = [55*mm, 95*mm, 30*mm]
    header = data[0]
    rows = data[1:]
    table_data = [[Paragraph(f'<b><font color="white" size="9">{h}</font></b>', S["body"]) for h in header]]
    for row in rows:
        styled = []
        for i, cell in enumerate(row):
            if i == 2:
                badge_color = GREEN if cell in ["✓ Oui", "✓ Inclus"] else GOLD if cell == "⚡ Clé" else BLUE
                bg = GREEN_BG if cell in ["✓ Oui", "✓ Inclus"] else GOLD_BG if cell == "⚡ Clé" else BLUE_BG
                p = Paragraph(f'<font size="8.5" color="#{badge_color.hexval()[1:]}"><b>{cell}</b></font>', 
                    ParagraphStyle("c", alignment=TA_CENTER, leading=11))
            elif i == 0:
                p = Paragraph(f'<b><font size="9.5" color="#0f172a">{cell}</font></b>', 
                    ParagraphStyle("c0", leading=13))
            else:
                p = Paragraph(f'<font size="9" color="#475569">{cell}</font>', 
                    ParagraphStyle("c1", leading=13))
            styled.append(p)
        table_data.append(styled)
    t = Table(table_data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), NAVY),
        ("BACKGROUND", (0,1), (-1,-1), WHITE),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [WHITE, GRAY_LIGHT]),
        ("ALIGN", (0,0), (-1,-1), "LEFT"),
        ("ALIGN", (2,0), (2,-1), "CENTER"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("LEFTPADDING", (0,0), (-1,-1), 10),
        ("RIGHTPADDING", (0,0), (-1,-1), 8),
        ("TOPPADDING", (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
        ("GRID", (0,0), (-1,-1), 0.4, GRAY_BORDER),
        ("LINEBELOW", (0,0), (-1,0), 2, PURPLE),
        ("ROUNDEDCORNERS", (0,0), (-1,-1), [4,4,4,4]),
    ]))
    return t

def stat_cards(stats):
    """stats = [(value, label, color), ...]"""
    cells = []
    for val, label, col in stats:
        inner = f'<font size="20" color="#{col.hexval()[1:]}"><b>{val}</b></font><br/><font size="8" color="#94a3b8">{label}</font>'
        p = Paragraph(inner, ParagraphStyle("sc", alignment=TA_CENTER, leading=26))
        cells.append(p)
    t = Table([cells], colWidths=[W/len(stats) - 6 for _ in stats])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), GRAY_DARK),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING", (0,0), (-1,-1), 14),
        ("BOTTOMPADDING", (0,0), (-1,-1), 14),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
        ("RIGHTPADDING", (0,0), (-1,-1), 8),
        ("INNERGRID", (0,0), (-1,-1), 0.4, colors.HexColor("#334155")),
        ("BOX", (0,0), (-1,-1), 0, WHITE),
        ("ROUNDEDCORNERS", (0,0), (-1,-1), [8,8,8,8]),
    ]))
    return t

# ─── BUILD ───────────────────────────────────────────────────────────────────
OUTPUT = "/mnt/user-data/outputs/Dunia_Rapport_Technique.pdf"

doc = BaseDocTemplate(
    OUTPUT,
    pagesize=A4,
    leftMargin=20*mm,
    rightMargin=20*mm,
    topMargin=45*mm,
    bottomMargin=22*mm,
)

cover_frame = Frame(0, 0, W, H, leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
normal_frame = Frame(20*mm, 22*mm, W - 40*mm, H - 67*mm, id="normal")

doc.addPageTemplates([
    PageTemplate(id="cover", frames=[cover_frame], onPage=cover_background),
    PageTemplate(id="normal", frames=[normal_frame], onPage=normal_page),
])

story = []

# ══════════════════════════════════════════════════════
# PAGE DE COUVERTURE
# ══════════════════════════════════════════════════════
story.append(Spacer(1, 60*mm))
story.append(Paragraph("DUNIA.", S["cover_title"]))
story.append(Spacer(1, 4*mm))
story.append(Paragraph("Rapport Technique", S["cover_sub"]))
story.append(Spacer(1, 3*mm))
story.append(Paragraph("Architecture · Stack · Fonctionnalités", S["cover_meta"]))
story.append(Spacer(1, 8*mm))

# Ligne décorative
sep = Table([[""]], colWidths=[60*mm])
sep.setStyle(TableStyle([
    ("LINEBELOW", (0,0), (-1,-1), 2, GOLD),
    ("TOPPADDING", (0,0), (-1,-1), 0),
    ("BOTTOMPADDING", (0,0), (-1,-1), 0),
]))
# Center it
centered_sep = Table([[sep]], colWidths=[W])
centered_sep.setStyle(TableStyle([("ALIGN",(0,0),(-1,-1),"CENTER"),("TOPPADDING",(0,0),(-1,-1),0),("BOTTOMPADDING",(0,0),(-1,-1),0)]))
story.append(centered_sep)
story.append(Spacer(1, 30*mm))

# Meta infos sur la couverture
meta_items = [
    ("Version", "1.0.0"),
    ("Date", datetime.date.today().strftime("%d %B %Y")),
    ("Équipe", "Dunia Dev Team"),
    ("Statut", "En développement"),
]
meta_data = [[
    Paragraph(f'<font size="8" color="#94a3b8">{k}</font><br/><font size="11" color="white"><b>{v}</b></font>',
              ParagraphStyle("m", alignment=TA_CENTER, leading=16))
    for k, v in meta_items
]]
meta_t = Table(meta_data, colWidths=[W/4]*4)
meta_t.setStyle(TableStyle([
    ("ALIGN",(0,0),(-1,-1),"CENTER"),
    ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
    ("TOPPADDING",(0,0),(-1,-1),12),
    ("BOTTOMPADDING",(0,0),(-1,-1),12),
    ("LINEBEFORE",(1,0),(-1,-1),0.5,colors.HexColor("#334155")),
]))
story.append(meta_t)
story.append(Spacer(1, 20*mm))

tags_data = [[
    Paragraph('<font size="9" color="#a78bfa">Frontend</font>', ParagraphStyle("t",alignment=TA_CENTER)),
    Paragraph('<font size="9" color="#f59e0b">Backend</font>', ParagraphStyle("t",alignment=TA_CENTER)),
    Paragraph('<font size="9" color="#34d399">Tailwind + DaisyUI</font>', ParagraphStyle("t",alignment=TA_CENTER)),
    Paragraph('<font size="9" color="#60a5fa">Django</font>', ParagraphStyle("t",alignment=TA_CENTER)),
    Paragraph('<font size="9" color="#f87171">RDC · 2025</font>', ParagraphStyle("t",alignment=TA_CENTER)),
]]
tags_t = Table(tags_data, colWidths=[W/5]*5)
tags_t.setStyle(TableStyle([
    ("BACKGROUND",(0,0),(-1,-1),colors.HexColor("#1e1b4b")),
    ("ALIGN",(0,0),(-1,-1),"CENTER"),
    ("TOPPADDING",(0,0),(-1,-1),7),
    ("BOTTOMPADDING",(0,0),(-1,-1),7),
    ("INNERGRID",(0,0),(-1,-1),0.5,colors.HexColor("#312e81")),
    ("BOX",(0,0),(-1,-1),0,WHITE),
]))
story.append(tags_t)

story.append(PageBreak())

# ══════════════════════════════════════════════════════
# CHANGER DE TEMPLATE
# ══════════════════════════════════════════════════════
from reportlab.platypus import NextPageTemplate
story.append(NextPageTemplate("normal"))
story.append(PageBreak())

# ══════════════════════════════════════════════════════
# TABLE DES MATIÈRES
# ══════════════════════════════════════════════════════
story += section_header("—", "Table des Matières")

toc_entries = [
    ("1", "Présentation du Projet", [
        ("1.1", "Vision et objectifs"),
        ("1.2", "Contexte et cible"),
        ("1.3", "Chiffres clés"),
    ]),
    ("2", "Architecture Générale", [
        ("2.1", "Schéma d'architecture"),
        ("2.2", "Stack technologique"),
        ("2.3", "Structure des fichiers"),
    ]),
    ("3", "Modules & Fonctionnalités", [
        ("3.1", "Module Publication"),
        ("3.2", "Module Challenge"),
        ("3.3", "Module Cours"),
    ]),
    ("4", "Système d'Authentification", [
        ("4.1", "Inscription"),
        ("4.2", "Connexion"),
        ("4.3", "Sécurité"),
    ]),
    ("5", "Pages & Interfaces", [
        ("5.1", "Page d'Accueil"),
        ("5.2", "Page Challenges"),
        ("5.3", "Composants UI"),
    ]),
    ("6", "Modèle de Données", [
        ("6.1", "Entités principales"),
        ("6.2", "Relations"),
    ]),
    ("7", "API & Backend Django", [
        ("7.1", "Endpoints REST"),
        ("7.2", "Modèles Django"),
    ]),
    ("8", "Roadmap & Évolutions", []),
]

for num, title, subs in toc_entries:
    row = Table([
        [Paragraph(f'<b>{num}.</b>', S["toc_item"]),
         Paragraph(title, S["toc_item"]),
         Paragraph(f'<font color="#7c3aed">····</font>', ParagraphStyle("d",alignment=TA_RIGHT,fontSize=9)),
         Paragraph(f'<b>{num}</b>', ParagraphStyle("pn",alignment=TA_RIGHT,fontSize=10,textColor=PURPLE))]
    ], colWidths=[12*mm, 100*mm, 40*mm, 18*mm])
    row.setStyle(TableStyle([
        ("ALIGN",(0,0),(-1,-1),"LEFT"),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("TOPPADDING",(0,0),(-1,-1),3),
        ("BOTTOMPADDING",(0,0),(-1,-1),3),
        ("LINEBELOW",(0,0),(-1,-1),0.3,GRAY_BORDER),
    ]))
    story.append(row)
    for sub_num, sub_title in subs:
        sub_row = Table([
            [Paragraph(f'{sub_num}', S["toc_sub"]),
             Paragraph(sub_title, S["toc_sub"]),
             Paragraph('', S["toc_sub"]),
             Paragraph('', S["toc_sub"])]
        ], colWidths=[12*mm, 100*mm, 40*mm, 18*mm])
        sub_row.setStyle(TableStyle([
            ("TOPPADDING",(0,0),(-1,-1),2),
            ("BOTTOMPADDING",(0,0),(-1,-1),2),
            ("LINEBELOW",(0,0),(-1,-1),0.2,GRAY_BORDER),
        ]))
        story.append(sub_row)

story.append(PageBreak())

# ══════════════════════════════════════════════════════
# SECTION 1 — PRÉSENTATION
# ══════════════════════════════════════════════════════
story += section_header("1", "Présentation du Projet")

story.append(Paragraph("1.1  Vision et Objectifs", S["h2"]))
story.append(Paragraph(
    "Dunia est une plateforme communautaire en ligne dédiée à la créativité, "
    "à l'apprentissage et à l'expression des talents africains. Le nom "
    "<b>Dunia</b> — qui signifie \"monde\" en swahili — reflète l'ambition "
    "d'une communauté panafricaine ouverte sur le monde. La plateforme s'articule "
    "autour de trois piliers fondamentaux : la Publication, le Challenge et les Cours.",
    S["body"]))

story.append(Spacer(1, 4*mm))
story.append(info_box("Objectifs Stratégiques", [
    "Offrir un espace de publication et de partage de contenus créatifs",
    "Stimuler la compétition saine via un système de Challenges communautaires",
    "Démocratiser l'accès aux connaissances via des Cours en ligne",
    "Valoriser les talents africains à l'échelle continentale et internationale",
    "Construire une économie créative numérique ancrée en Afrique centrale",
], PURPLE, PURPLE_BG))
story.append(Spacer(1, 4*mm))

story.append(Paragraph("1.2  Contexte et Cible", S["h2"]))
story.append(Paragraph(
    "La plateforme cible en priorité la jeunesse africaine francophone (15–35 ans), "
    "avec un focus initial sur la République Démocratique du Congo, puis une extension "
    "progressive vers l'Afrique subsaharienne francophone. La plateforme est conçue "
    "pour fonctionner sur des connexions internet limitées, avec une optimisation "
    "mobile-first pour s'adapter au contexte local.",
    S["body"]))

story.append(Spacer(1, 4*mm))
story.append(Paragraph("1.3  Chiffres Clés (Projections Année 1)", S["h2"]))
story.append(Spacer(1, 3*mm))
story.append(stat_cards([
    ("3", "Modules principaux", PURPLE),
    ("5", "Types de contenu", GOLD),
    ("20+", "Endpoints API", BLUE),
    ("8", "Modèles Django", GREEN),
    ("100%", "Responsive", RED),
]))
story.append(Spacer(1, 6*mm))
story.append(PageBreak())

# ══════════════════════════════════════════════════════
# SECTION 2 — ARCHITECTURE
# ══════════════════════════════════════════════════════
story += section_header("2", "Architecture Générale")

story.append(Paragraph("2.1  Schéma d'Architecture", S["h2"]))
story.append(Paragraph(
    "Dunia adopte une architecture <b>Client-Serveur</b> classique avec séparation "
    "nette entre le frontend (rendu HTML/CSS/JS via les templates Django) et le backend "
    "(Django REST Framework pour les données). Cette approche garantit la maintenabilité "
    "et permet une évolution vers une API-first si nécessaire.",
    S["body"]))

story.append(Spacer(1, 4*mm))

# Architecture diagram as table
arch_layers = [
    ("🖥️  NAVIGATEUR CLIENT", "HTML5 · CSS3 · JavaScript Vanilla", PURPLE_BG, PURPLE),
    ("🎨  FRONTEND LAYER", "Tailwind CSS + DaisyUI · Templates Django · Design System Dunia", BLUE_BG, BLUE),
    ("⚙️  BACKEND LAYER", "Django 4.x · Django REST Framework · Authentification JWT", GOLD_BG, GOLD),
    ("🗄️  DATA LAYER", "PostgreSQL (prod) · SQLite (dev) · Migrations Django · ORM", GREEN_BG, GREEN),
    ("☁️  INFRASTRUCTURE", "Serveur Linux · Nginx · Gunicorn · Déploiement (à définir)", GRAY_LIGHT, GRAY_MID),
]
for icon_label, detail, bg, col in arch_layers:
    row = Table([[
        Paragraph(f'<b><font size="9">{icon_label}</font></b>',
            ParagraphStyle("al", fontName="Helvetica-Bold", fontSize=9, textColor=col, leading=12)),
        Paragraph(f'<font size="9" color="#475569">{detail}</font>',
            ParagraphStyle("ad", fontSize=9, leading=13)),
    ]], colWidths=[62*mm, 105*mm])
    row.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (0,0), bg),
        ("BACKGROUND", (1,0), (1,0), WHITE),
        ("LINEBELOW", (0,0), (-1,-1), 0.5, col),
        ("LINELEFT", (0,0), (0,0), 3, col),
        ("TOPPADDING", (0,0), (-1,-1), 10),
        ("BOTTOMPADDING", (0,0), (-1,-1), 10),
        ("LEFTPADDING", (0,0), (-1,-1), 12),
        ("RIGHTPADDING", (0,0), (-1,-1), 10),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ]))
    story.append(row)
    story.append(Spacer(1, 1.5*mm))

story.append(Spacer(1, 5*mm))
story.append(Paragraph("2.2  Stack Technologique", S["h2"]))
story.append(Spacer(1, 3*mm))

stack_data = [
    ["Composant", "Technologie", "Rôle"],
    ["Frontend — Structure", "HTML5 sémantique", "Markup des pages"],
    ["Frontend — Style", "Tailwind CSS v3", "Utility-first CSS"],
    ["Frontend — UI", "DaisyUI v4", "Composants prêts à l'emploi"],
    ["Frontend — Scripts", "JavaScript Vanilla (ES6+)", "Interactivité, modals, AJAX"],
    ["Backend — Framework", "Django 4.x (Python)", "Logique serveur, vues, URLs"],
    ["Backend — API", "Django REST Framework", "Endpoints JSON pour le frontend"],
    ["Authentification", "Django Auth + JWT", "Sessions, tokens, sécurité"],
    ["Base de données", "PostgreSQL / SQLite", "Stockage persistant"],
    ["Serveur WSGI", "Gunicorn", "Serveur d'application Python"],
    ["Reverse Proxy", "Nginx", "Gestion des requêtes HTTP"],
    ["Gestion des médias", "Django Storage + S3", "Upload images, fichiers"],
    ["Typographie", "Syne (titres) · DM Sans (corps)", "Identité visuelle Dunia"],
]
story.append(feature_table(stack_data,
    col_widths=[55*mm, 60*mm, 55*mm]))
story.append(Spacer(1, 5*mm))

story.append(Paragraph("2.3  Structure des Fichiers (Django)", S["h2"]))
story.append(Spacer(1, 2*mm))

code_lines = [
    "dunia/",
    "├── manage.py",
    "├── dunia_project/          # Configuration principale",
    "│   ├── settings.py",
    "│   ├── urls.py",
    "│   └── wsgi.py",
    "├── apps/",
    "│   ├── accounts/           # Authentification & Profils",
    "│   │   ├── models.py       # User, Profile",
    "│   │   ├── views.py        # Login, Register, Logout",
    "│   │   └── urls.py",
    "│   ├── publications/       # Publications & Feed",
    "│   │   ├── models.py       # Post, Like, Comment",
    "│   │   ├── views.py",
    "│   │   └── serializers.py",
    "│   ├── challenges/         # Challenges & Critiques",
    "│   │   ├── models.py       # Challenge, Submission, Critique, Winner",
    "│   │   ├── views.py",
    "│   │   └── serializers.py",
    "│   └── cours/              # Cours & Modules",
    "│       ├── models.py       # Course, Module, Enrollment",
    "│       └── views.py",
    "├── templates/              # Templates HTML Django",
    "│   ├── base.html",
    "│   ├── auth/",
    "│   ├── home/",
    "│   ├── challenges/",
    "│   └── cours/",
    "└── static/                 # CSS, JS, images",
    "    ├── css/",
    "    ├── js/",
    "    └── img/",
]

code_block = "\n".join(code_lines)
code_p = Paragraph(code_block.replace("\n","<br/>").replace(" ","&nbsp;"), S["code"])
code_t = Table([[code_p]], colWidths=[W - 40*mm])
code_t.setStyle(TableStyle([
    ("BACKGROUND",(0,0),(-1,-1),GRAY_LIGHT),
    ("LEFTPADDING",(0,0),(-1,-1),14),
    ("RIGHTPADDING",(0,0),(-1,-1),14),
    ("TOPPADDING",(0,0),(-1,-1),12),
    ("BOTTOMPADDING",(0,0),(-1,-1),12),
    ("LINELEFT",(0,0),(0,-1),3,PURPLE),
    ("BOX",(0,0),(-1,-1),0.5,GRAY_BORDER),
    ("ROUNDEDCORNERS",(0,0),(-1,-1),[4,4,4,4]),
]))
story.append(code_t)
story.append(PageBreak())

# ══════════════════════════════════════════════════════
# SECTION 3 — MODULES
# ══════════════════════════════════════════════════════
story += section_header("3", "Modules & Fonctionnalités")

# Module 1 — Publication
story.append(Paragraph("3.1  Module Publication", S["h2"]))
story.append(Paragraph(
    "Le module Publication constitue le cœur social de Dunia. Il permet à tout "
    "utilisateur inscrit de partager du contenu (texte, images, liens) avec la "
    "communauté. Les publications apparaissent dans le fil d'actualités personnalisé.",
    S["body"]))
story.append(Spacer(1, 3*mm))

pub_data = [
    ["Fonctionnalité", "Description", "Statut"],
    ["Créer une publication", "Post texte + images + hashtags dans le fil d'actualité", "✓ Inclus"],
    ["Fil d'actualité (Feed)", "Affichage chronologique et algorithmique des posts", "✓ Inclus"],
    ["Likes & Réactions", "Système de réactions emoji sur chaque publication", "✓ Inclus"],
    ["Commentaires", "Fil de discussion sous chaque publication", "✓ Inclus"],
    ["Hashtags", "Système de tags pour catégoriser et découvrir le contenu", "✓ Inclus"],
    ["Partage", "Partage interne et vers réseaux sociaux externes", "✓ Inclus"],
    ["Sauvegarde", "Marquer des publications pour y revenir plus tard", "✓ Inclus"],
    ["Signalement", "Modération communautaire — signaler un contenu inapproprié", "✓ Inclus"],
]
story.append(feature_table(pub_data))
story.append(Spacer(1, 5*mm))

# Module 2 — Challenge
story.append(Paragraph("3.2  Module Challenge", S["h2"]))
story.append(Paragraph(
    "Le module Challenge est la fonctionnalité différenciante de Dunia. Il permet "
    "à tout membre de créer et lancer des défis créatifs à la communauté, avec un "
    "système complet de soumissions, de critiques constructives et de proclamation "
    "des gagnants.",
    S["body"]))
story.append(Spacer(1, 3*mm))

challenge_data = [
    ["Fonctionnalité", "Description", "Statut"],
    ["Créer un Challenge", "Formulaire complet : titre, thème, description, image, dates, nombre de gagnants", "⚡ Clé"],
    ["Nombre de participants", "Compteur temps-réel des participants inscrits au challenge", "✓ Inclus"],
    ["Date & Heure", "Horodatage précis début/fin avec compte à rebours automatique", "✓ Inclus"],
    ["Thème du challenge", "Catégorisation par domaine : Design, Écriture, Musique, Code…", "✓ Inclus"],
    ["Image de couverture", "Upload d'une image représentative du challenge", "✓ Inclus"],
    ["Détails & Règles", "Description longue avec les règles et critères d'évaluation", "✓ Inclus"],
    ["Espace de Critiques", "Section dédiée aux retours constructifs sur les soumissions", "⚡ Clé"],
    ["Votes communautaires", "Système de vote 👍👎 pour élire les meilleures soumissions", "⚡ Clé"],
    ["Tags de critique", "Catégories : Positif / Amélioration / Question", "✓ Inclus"],
    ["Transition vers critiques", "Bloc challenge cliquable qui navigue vers l'espace critique", "⚡ Clé"],
    ["Proclamation gagnants", "Annonce automatique des gagnants après expiration du délai", "⚡ Clé"],
    ["Badges gagnants", "Attribution de badges 🥇🥈🥉 sur le profil des gagnants", "✓ Inclus"],
    ["Statuts du challenge", "En cours / À venir / Terminé avec indicateurs visuels", "✓ Inclus"],
]
story.append(feature_table(challenge_data))
story.append(Spacer(1, 5*mm))

# Module 3 — Cours
story.append(Paragraph("3.3  Module Cours", S["h2"]))
story.append(Paragraph(
    "Le module Cours transforme Dunia en plateforme d'apprentissage peer-to-peer. "
    "N'importe quel membre peut créer et partager ses connaissances sous forme de "
    "cours structurés en modules progressifs.",
    S["body"]))
story.append(Spacer(1, 3*mm))

cours_data = [
    ["Fonctionnalité", "Description", "Statut"],
    ["Créer un cours", "Titre, description, catégorie, durée, niveau de difficulté", "✓ Inclus"],
    ["Modules & Chapitres", "Structure en modules progressifs avec contenu riche", "✓ Inclus"],
    ["Inscription", "Système d'inscription au cours avec suivi de progression", "✓ Inclus"],
    ["Barre de progression", "Indicateur visuel de l'avancement dans le cours", "✓ Inclus"],
    ["Commentaires & Q&A", "Section de questions-réponses par chapitre", "✓ Inclus"],
    ["Certificat de fin", "Attestation numérique à l'issue du cours complet", "✓ Inclus"],
    ["Évaluations", "Système de notation et avis sur les cours", "✓ Inclus"],
]
story.append(feature_table(cours_data))
story.append(PageBreak())

# ══════════════════════════════════════════════════════
# SECTION 4 — AUTHENTIFICATION
# ══════════════════════════════════════════════════════
story += section_header("4", "Système d'Authentification")

story.append(Paragraph("4.1  Inscription (Register)", S["h2"]))
story.append(Paragraph(
    "La page d'inscription collecte les informations minimales nécessaires pour "
    "créer un compte Dunia. Tous les champs sont validés côté client (JavaScript) "
    "et côté serveur (Django).",
    S["body"]))
story.append(Spacer(1, 3*mm))

auth_register = [
    ["Champ", "Type", "Statut"],
    ["Prénom", "Texte requis — min. 2 caractères", "✓ Inclus"],
    ["Nom", "Texte requis — min. 2 caractères", "✓ Inclus"],
    ["Nom d'utilisateur (@)", "Unique, alphanumérique, min. 3 caractères", "✓ Inclus"],
    ["Adresse email", "Format email valide, unicité vérifiée en base", "✓ Inclus"],
    ["Mot de passe", "Min. 8 caractères, indicateur de force", "✓ Inclus"],
    ["Confirmation MDP", "Vérification de correspondance des deux champs", "✓ Inclus"],
    ["CGU / Politique", "Case à cocher obligatoire avant soumission", "✓ Inclus"],
]
story.append(feature_table(auth_register))
story.append(Spacer(1, 5*mm))

story.append(Paragraph("4.2  Connexion (Login)", S["h2"]))
story.append(Paragraph(
    "La connexion s'effectue par email/mot de passe avec option de connexion "
    "sociale via Google et Facebook pour simplifier l'expérience utilisateur.",
    S["body"]))
story.append(Spacer(1, 3*mm))

auth_login = [
    ["Méthode", "Description", "Statut"],
    ["Email + Mot de passe", "Authentification classique avec gestion d'erreurs", "✓ Inclus"],
    ["Connexion Google", "OAuth 2.0 via django-allauth", "✓ Inclus"],
    ["Connexion Facebook", "OAuth 2.0 via django-allauth", "✓ Inclus"],
    ["Mot de passe oublié", "Reset par email avec lien sécurisé (24h)", "✓ Inclus"],
    ["Remember me", "Session persistante 30 jours", "✓ Inclus"],
]
story.append(feature_table(auth_login))
story.append(Spacer(1, 5*mm))

story.append(Paragraph("4.3  Sécurité", S["h2"]))
story.append(info_box("Mesures de Sécurité Implémentées", [
    "Protection CSRF intégrée Django sur tous les formulaires",
    "Hachage des mots de passe avec PBKDF2 (algorithme par défaut Django)",
    "Tokens JWT pour l'authentification API (accès + refresh tokens)",
    "Rate limiting sur les endpoints de connexion (anti-brute force)",
    "Validation et sanitation de toutes les entrées utilisateur côté serveur",
    "HTTPS obligatoire en production (TLS 1.2+)",
], PURPLE, PURPLE_BG))
story.append(PageBreak())

# ══════════════════════════════════════════════════════
# SECTION 5 — PAGES & INTERFACES
# ══════════════════════════════════════════════════════
story += section_header("5", "Pages & Interfaces")

story.append(Paragraph("5.1  Page d'Accueil (Feed)", S["h2"]))
story.append(Paragraph(
    "La page d'accueil adopte un layout tri-colonnes inspiré des grandes plateformes "
    "sociales (sidebar gauche, fil central, sidebar droite) pour maximiser la densité "
    "d'information tout en restant lisible sur tous les écrans.",
    S["body"]))
story.append(Spacer(1, 3*mm))

home_data = [
    ["Zone", "Contenu", "Statut"],
    ["Sidebar Gauche", "Navigation principale : Accueil, Challenges, Cours, Notifs, Profil + bouton Publier", "✓ Inclus"],
    ["Topbar", "Barre de recherche globale, bouton Publier mobile, notifications", "✓ Inclus"],
    ["Fil central", "Publications, Challenges, Cours triés par date + algorithme", "✓ Inclus"],
    ["Filtres de contenu", "Tabs : Tout / Publications / Challenges / Cours / Tendances", "✓ Inclus"],
    ["Bloc création rapide", "Zone de publication rapide avec options Photo / Challenge / Cours", "✓ Inclus"],
    ["Sidebar droite", "Challenges en direct (avec indicateur live), Tendances, Suggestions d'abonnement", "✓ Inclus"],
]
story.append(feature_table(home_data, col_widths=[42*mm, 100*mm, 28*mm]))
story.append(Spacer(1, 5*mm))

story.append(Paragraph("5.2  Page Challenges", S["h2"]))
story.append(Paragraph(
    "La page Challenges est structurée pour maximiser la participation. Un hero "
    "section avec des statistiques globales donne une vue d'ensemble, suivi d'une "
    "grille de challenges filtrables.",
    S["body"]))
story.append(Spacer(1, 3*mm))

challenge_page_data = [
    ["Élément", "Description", "Statut"],
    ["Hero Section", "Statistiques globales : challenges actifs, participants, gagnants, pays", "✓ Inclus"],
    ["Challenge Vedette", "Challenge mis en avant avec layout étendu et accès rapide", "✓ Inclus"],
    ["Grille de challenges", "Cards challenges : En cours / À venir / Terminés avec gagnants", "✓ Inclus"],
    ["Filtres & Catégories", "Filtre par statut et par thème (Design, Écriture, Musique, Code…)", "✓ Inclus"],
    ["Modal Créer Challenge", "Formulaire complet dans une modal : titre, thème, dates, image, gagnants", "⚡ Clé"],
    ["Modal Détail Challenge", "Vue complète avec stats, description, règles, organisateur", "⚡ Clé"],
    ["Espace Critiques (modal)", "Formulaire de critique + liste des critiques avec votes", "⚡ Clé"],
    ["Proclamation gagnants", "Section dédiée sur les challenges terminés avec podium 🥇🥈🥉", "⚡ Clé"],
    ["Barre de progression", "Indicateur visuel du temps écoulé vs durée totale du challenge", "✓ Inclus"],
]
story.append(feature_table(challenge_page_data, col_widths=[48*mm, 95*mm, 27*mm]))
story.append(Spacer(1, 5*mm))

story.append(Paragraph("5.3  Design System & Composants UI", S["h2"]))
story.append(Paragraph(
    "Dunia possède une identité visuelle forte et cohérente appliquée sur toutes les pages.",
    S["body"]))
story.append(Spacer(1, 3*mm))

design_data = [
    ["Élément", "Valeur / Description", "Statut"],
    ["Couleur primaire", "Navy #0f172a — fond principal", "✓ Inclus"],
    ["Couleur accent", "Purple #7c3aed — actions, CTA, liens", "✓ Inclus"],
    ["Couleur highlight", "Gold #f59e0b — éléments de distinction", "✓ Inclus"],
    ["Typographie titres", "Syne Bold/ExtraBold — headers, boutons", "✓ Inclus"],
    ["Typographie corps", "DM Sans Regular/Medium — contenu, labels", "✓ Inclus"],
    ["Effet Glassmorphism", "backdrop-filter: blur() sur les cards de la page auth", "✓ Inclus"],
    ["Dark theme", "Thème sombre par défaut, compatible DaisyUI", "✓ Inclus"],
    ["Responsive design", "Mobile-first, breakpoints Tailwind (sm/md/lg/xl)", "✓ Inclus"],
    ["Animations", "fadeUp sur les cards, pulse sur les indicateurs live", "✓ Inclus"],
    ["Avatar ring", "Gradient purple-gold autour des avatars utilisateurs", "✓ Inclus"],
]
story.append(feature_table(design_data, col_widths=[48*mm, 90*mm, 32*mm]))
story.append(PageBreak())

# ══════════════════════════════════════════════════════
# SECTION 6 — MODÈLE DE DONNÉES
# ══════════════════════════════════════════════════════
story += section_header("6", "Modèle de Données")

story.append(Paragraph("6.1  Entités Principales", S["h2"]))
story.append(Paragraph(
    "Le modèle de données de Dunia est organisé autour de 8 entités principales "
    "gérées par l'ORM Django. Chaque entité correspond à une app Django distincte "
    "pour assurer la séparation des responsabilités.",
    S["body"]))
story.append(Spacer(1, 3*mm))

entities = [
    ("User (Utilisateur)", PURPLE, [
        "id, username, email, password_hash",
        "first_name, last_name, avatar",
        "bio, location, created_at",
        "is_verified, followers_count",
    ]),
    ("Post (Publication)", BLUE, [
        "id, author (FK User), content",
        "images, hashtags, created_at",
        "likes_count, comments_count",
        "post_type (publication/challenge/cours)",
    ]),
    ("Challenge", GOLD, [
        "id, creator (FK User), title, theme",
        "description, cover_image",
        "start_date, end_date, winner_count",
        "status (draft/active/closed)",
        "participants_count",
    ]),
    ("Submission (Soumission)", GREEN, [
        "id, challenge (FK Challenge)",
        "author (FK User), content, files",
        "submitted_at, votes_count",
        "is_winner, rank",
    ]),
    ("Critique", RED, [
        "id, challenge (FK Challenge)",
        "author (FK User), content",
        "critique_type (positive/improvement/question)",
        "upvotes, downvotes, created_at",
    ]),
    ("Course (Cours)", colors.HexColor("#8b5cf6"), [
        "id, instructor (FK User), title",
        "description, cover_image, duration",
        "difficulty (beginner/intermediate/advanced)",
        "modules_count, enrollments_count",
    ]),
    ("Module", colors.HexColor("#06b6d4"), [
        "id, course (FK Course), title",
        "content, order, duration",
        "video_url, resources",
    ]),
    ("Enrollment (Inscription)", colors.HexColor("#ec4899"), [
        "id, user (FK User), course (FK Course)",
        "enrolled_at, progress_percent",
        "completed_modules, is_completed",
        "certificate_issued_at",
    ]),
]

for entity_name, col, fields in entities:
    fields_text = "<br/>".join([f'<font size="8.5" color="#475569">• {f}</font>' for f in fields])
    p_name = Paragraph(f'<b><font size="10">{entity_name}</font></b>',
        ParagraphStyle("en", fontName="Helvetica-Bold", fontSize=10, textColor=col, leading=14))
    p_fields = Paragraph(fields_text, ParagraphStyle("ef", fontSize=8.5, leading=13))
    row = Table([[p_name, p_fields]], colWidths=[55*mm, 110*mm])
    row.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (0,0), colors.HexColor(f"#{col.hexval()[1:]}15") if hasattr(col, 'hexval') else PURPLE_BG),
        ("BACKGROUND", (1,0), (1,0), WHITE),
        ("LINELEFT", (0,0), (0,0), 3, col),
        ("LINEBELOW", (0,0), (-1,-1), 0.4, GRAY_BORDER),
        ("TOPPADDING", (0,0), (-1,-1), 10),
        ("BOTTOMPADDING", (0,0), (-1,-1), 10),
        ("LEFTPADDING", (0,0), (-1,-1), 12),
        ("RIGHTPADDING", (0,0), (-1,-1), 10),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
    ]))
    story.append(row)
    story.append(Spacer(1, 1.5*mm))

story.append(Spacer(1, 5*mm))
story.append(Paragraph("6.2  Relations Clés", S["h2"]))
story.append(info_box("Dépendances entre entités", [
    "User → Post : One-to-Many (un utilisateur peut avoir plusieurs publications)",
    "User → Challenge : One-to-Many (un utilisateur peut créer plusieurs challenges)",
    "Challenge → Submission : One-to-Many (un challenge a plusieurs soumissions)",
    "Challenge → Critique : One-to-Many (un challenge a plusieurs critiques)",
    "User ↔ User : Many-to-Many (système de followers/following)",
    "User ↔ Course : Many-to-Many via Enrollment (inscriptions aux cours)",
    "Course → Module : One-to-Many (un cours est découpé en modules)",
], PURPLE, PURPLE_BG))
story.append(PageBreak())

# ══════════════════════════════════════════════════════
# SECTION 7 — API & BACKEND
# ══════════════════════════════════════════════════════
story += section_header("7", "API & Backend Django")

story.append(Paragraph("7.1  Endpoints REST Principaux", S["h2"]))
story.append(Paragraph(
    "L'API Django REST Framework expose les endpoints suivants. "
    "Tous les endpoints protégés nécessitent un token JWT valide "
    "dans le header <b>Authorization: Bearer &lt;token&gt;</b>.",
    S["body"]))
story.append(Spacer(1, 3*mm))

api_data = [
    ["Endpoint", "Méthode", "Description"],
    ["/api/auth/register/", "POST", "Créer un nouveau compte utilisateur"],
    ["/api/auth/login/", "POST", "Authentification — retourne access + refresh tokens"],
    ["/api/auth/refresh/", "POST", "Rafraîchir le token d'accès expiré"],
    ["/api/users/{id}/", "GET / PATCH", "Voir ou modifier un profil utilisateur"],
    ["/api/posts/", "GET / POST", "Lister le feed ou créer une publication"],
    ["/api/posts/{id}/like/", "POST", "Liker / unliker une publication"],
    ["/api/challenges/", "GET / POST", "Lister tous les challenges ou en créer un"],
    ["/api/challenges/{id}/", "GET / PUT / DELETE", "Détail, modifier ou supprimer un challenge"],
    ["/api/challenges/{id}/submit/", "POST", "Soumettre une participation à un challenge"],
    ["/api/challenges/{id}/critiques/", "GET / POST", "Lister ou ajouter une critique"],
    ["/api/critiques/{id}/vote/", "POST", "Voter pour une critique (upvote/downvote)"],
    ["/api/challenges/{id}/winners/", "POST", "Proclamer les gagnants (organisateur only)"],
    ["/api/courses/", "GET / POST", "Lister les cours ou en créer un nouveau"],
    ["/api/courses/{id}/enroll/", "POST", "S'inscrire à un cours"],
    ["/api/courses/{id}/progress/", "PATCH", "Mettre à jour la progression dans un cours"],
]
story.append(feature_table(api_data, col_widths=[65*mm, 28*mm, 77*mm]))
story.append(Spacer(1, 5*mm))

story.append(Paragraph("7.2  Extrait Modèles Django", S["h2"]))
story.append(Spacer(1, 2*mm))

model_code = [
    "# apps/challenges/models.py",
    "",
    "class Challenge(models.Model):",
    "    THEME_CHOICES = [('design','Design'), ('ecriture','Écriture'),",
    "                     ('musique','Musique'), ('code','Code')]",
    "    STATUS_CHOICES = [('draft','Brouillon'), ('active','En cours'),",
    "                      ('closed','Terminé')]",
    "",
    "    creator      = models.ForeignKey(User, on_delete=models.CASCADE)",
    "    title        = models.CharField(max_length=200)",
    "    theme        = models.CharField(max_length=50, choices=THEME_CHOICES)",
    "    description  = models.TextField()",
    "    cover_image  = models.ImageField(upload_to='challenges/')",
    "    start_date   = models.DateTimeField()",
    "    end_date     = models.DateTimeField()",
    "    winner_count = models.IntegerField(default=3)",
    "    status       = models.CharField(max_length=20, choices=STATUS_CHOICES)",
    "    created_at   = models.DateTimeField(auto_now_add=True)",
    "",
    "    def is_active(self):",
    "        return self.status == 'active' and self.end_date > timezone.now()",
    "",
    "class Critique(models.Model):",
    "    TYPE_CHOICES = [('positive','Positif'), ('improvement','Amélioration'),",
    "                    ('question','Question')]",
    "    challenge    = models.ForeignKey(Challenge, on_delete=models.CASCADE)",
    "    author       = models.ForeignKey(User, on_delete=models.CASCADE)",
    "    content      = models.TextField()",
    "    critique_type = models.CharField(max_length=20, choices=TYPE_CHOICES)",
    "    upvotes      = models.IntegerField(default=0)",
    "    downvotes    = models.IntegerField(default=0)",
    "    created_at   = models.DateTimeField(auto_now_add=True)",
]
code_text = "<br/>".join([l.replace(" ", "&nbsp;").replace("<","&lt;").replace(">","&gt;") for l in model_code])
cp = Paragraph(code_text, S["code"])
ct = Table([[cp]], colWidths=[W - 40*mm])
ct.setStyle(TableStyle([
    ("BACKGROUND",(0,0),(-1,-1),colors.HexColor("#0f172a")),
    ("LEFTPADDING",(0,0),(-1,-1),14),
    ("RIGHTPADDING",(0,0),(-1,-1),14),
    ("TOPPADDING",(0,0),(-1,-1),12),
    ("BOTTOMPADDING",(0,0),(-1,-1),12),
    ("LINELEFT",(0,0),(0,-1),3,PURPLE),
    ("BOX",(0,0),(-1,-1),0.5,colors.HexColor("#1e293b")),
    ("ROUNDEDCORNERS",(0,0),(-1,-1),[4,4,4,4]),
]))
# Override text color for dark background
code_dark = ParagraphStyle("code_dark",
    fontName="Courier", fontSize=8, textColor=colors.HexColor("#a78bfa"),
    leading=13, leftIndent=0)
cp2 = Paragraph(code_text, code_dark)
ct2 = Table([[cp2]], colWidths=[W - 40*mm])
ct2.setStyle(TableStyle([
    ("BACKGROUND",(0,0),(-1,-1),colors.HexColor("#0f172a")),
    ("LEFTPADDING",(0,0),(-1,-1),14),
    ("RIGHTPADDING",(0,0),(-1,-1),14),
    ("TOPPADDING",(0,0),(-1,-1),12),
    ("BOTTOMPADDING",(0,0),(-1,-1),12),
    ("LINELEFT",(0,0),(0,-1),3,PURPLE),
    ("BOX",(0,0),(-1,-1),0.5,colors.HexColor("#1e293b")),
]))
story.append(ct2)
story.append(PageBreak())

# ══════════════════════════════════════════════════════
# SECTION 8 — ROADMAP
# ══════════════════════════════════════════════════════
story += section_header("8", "Roadmap & Évolutions")

story.append(Paragraph("8.1  Phases de Développement", S["h2"]))
story.append(Spacer(1, 3*mm))

phases = [
    ("Phase 1", "MVP — Fondations", "Mois 1–2", PURPLE, [
        "Mise en place Django + PostgreSQL + authentification",
        "Pages Auth (inscription/connexion) complètes",
        "Page d'accueil avec fil de publications de base",
        "Système de likes et commentaires simples",
    ]),
    ("Phase 2", "Module Challenge", "Mois 3–4", GOLD, [
        "Création et gestion des challenges",
        "Soumissions et espace de critiques",
        "Système de votes communautaires",
        "Proclamation automatique des gagnants",
    ]),
    ("Phase 3", "Module Cours", "Mois 5–6", GREEN, [
        "Création et publication de cours en modules",
        "Système d'inscription et de suivi de progression",
        "Certificats numériques à la complétion",
        "Système de notation et avis",
    ]),
    ("Phase 4", "Croissance & Perf.", "Mois 7–9", BLUE, [
        "Algorithme de recommandation de contenu",
        "Notifications push et par email",
        "Application mobile (React Native ou PWA)",
        "Monétisation : abonnements premium, cours payants",
    ]),
]

for phase_num, phase_title, timeline, col, items in phases:
    items_text = "<br/>".join([f'<font size="9" color="#475569">  → {item}</font>' for item in items])
    header_p = Paragraph(
        f'<font size="10" color="white"><b>{phase_num}</b></font>  '
        f'<font size="11" color="white"><b>{phase_title}</b></font>'
        f'<br/><font size="8.5" color="#94a3b8">{timeline}</font>',
        ParagraphStyle("ph", fontName="Helvetica", fontSize=10, leading=16))
    items_p = Paragraph(items_text, ParagraphStyle("pi", fontSize=9, leading=16))
    row = Table([[header_p, items_p]], colWidths=[55*mm, 112*mm])
    row.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (0,0), NAVY),
        ("BACKGROUND", (1,0), (1,0), WHITE),
        ("LINELEFT", (0,0), (0,0), 4, col),
        ("LINEBELOW", (0,0), (-1,-1), 0.5, GRAY_BORDER),
        ("TOPPADDING", (0,0), (-1,-1), 12),
        ("BOTTOMPADDING", (0,0), (-1,-1), 12),
        ("LEFTPADDING", (0,0), (-1,-1), 14),
        ("RIGHTPADDING", (0,0), (-1,-1), 10),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
    ]))
    story.append(row)
    story.append(Spacer(1, 2*mm))

story.append(Spacer(1, 6*mm))
story.append(info_box("Évolutions Post-Lancement Envisagées", [
    "Marketplace : vente de templates, assets, services entre créatifs",
    "Streaming live : challenges en temps réel avec audience",
    "IA de recommandation : suggestions personnalisées de challenges et cours",
    "Réseau d'entreprises : partenariats pour des challenges sponsorisés",
    "API publique : permettre à des tiers d'intégrer Dunia dans leurs apps",
    "Expansion : version anglophone pour l'Afrique anglophone et diaspora",
], GREEN, GREEN_BG))

story.append(Spacer(1, 8*mm))
story.append(hr(PURPLE, 1))
story.append(Spacer(1, 4*mm))
story.append(Paragraph(
    "Ce rapport technique a été généré automatiquement à partir des spécifications "
    "du projet Dunia. Il est destiné à l'équipe de développement et aux parties prenantes "
    "techniques du projet.",
    ParagraphStyle("end", fontName="Helvetica-Oblique", fontSize=9, textColor=GRAY_MID,
        alignment=TA_CENTER, leading=14)))
story.append(Spacer(1, 2*mm))
story.append(Paragraph(
    f"Dunia Platform · Kinshasa, RDC · {datetime.date.today().strftime('%B %Y')}",
    ParagraphStyle("end2", fontName="Helvetica-Bold", fontSize=9, textColor=PURPLE,
        alignment=TA_CENTER)))

# ── BUILD ─────────────────────────────────────────────
doc.build(story)
print(f"✅  PDF généré : {OUTPUT}")