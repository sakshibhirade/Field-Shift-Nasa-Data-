# app.py - Field Shift: Professional Agricultural Decision-Support Platform
# Run with:  streamlit run app.py
# It only CALLS scoring.py. It must never change a number or a weight.

import streamlit as st
import scoring as sc
import re

st.set_page_config(
    page_title="Field Shift — Crop Rotation Helper",
    page_icon="🌾",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# =====================================================================
# CUSTOM CSS — Professional mobile-first design
# =====================================================================
st.markdown("""
<style>
/* ── Import Noto Sans Kannada for proper rendering ── */
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Kannada:wght@400;500;600;700;800&family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── Root variables ── */
:root {
    --forest-green:       #2A5C2A;
    --forest-green-dark:  #1B3D1B;
    --forest-green-mid:   #3A6E3A;
    --sage-green:         #6B8F5E;
    --sage-light:         #9BBD8D;
    --sage-pale:          #C8DFBC;
    --sage-ultra-pale:    #EBF3E6;
    --warm-white:         #F8F6F1;
    --off-white:          #F2EDE5;
    --card-white:         #FFFFFF;
    --text-primary:       #182818;
    --text-secondary:     #3D5240;
    --text-muted:         #4A6052;
    --text-light:         #526E59;
    --border-light:       #DDE8D7;
    --border-mid:         #C4D9BB;
    --warning-bg:         #FFFBEE;
    --warning-border:     #D4A017;
    --warning-text:       #6B4F00;
    --success-bg:         #EBF5EC;
    --success-border:     #3D9A42;
    --info-bg:            #E8F2FC;
    --info-border:        #3A87CC;
    --shadow-xs:          0 1px 2px rgba(0,0,0,0.05);
    --shadow-sm:          0 2px 6px rgba(0,0,0,0.07), 0 1px 2px rgba(0,0,0,0.04);
    --shadow-md:          0 4px 16px rgba(0,0,0,0.09), 0 2px 5px rgba(0,0,0,0.05);
    --shadow-lg:          0 12px 32px rgba(0,0,0,0.11), 0 4px 10px rgba(0,0,0,0.05);
    --shadow-green:       0 6px 20px rgba(42,92,42,0.22);
    --radius-sm:          8px;
    --radius-md:          14px;
    --radius-lg:          18px;
    --radius-xl:          24px;
    --transition:         all 0.22s cubic-bezier(0.4, 0, 0.2, 1);
}

/* ── Global body & scrollbar ── */
.stApp {
    background-color: var(--warm-white) !important;
    font-family: 'Inter', 'Noto Sans Kannada', sans-serif !important;
}
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--warm-white); }
::-webkit-scrollbar-thumb { background: var(--sage-pale); border-radius: 3px; }

/* Hide default Streamlit chrome */
header[data-testid="stHeader"] {
    background: transparent !important;
    height: 0px !important;
    min-height: 0px !important;
}
footer { display: none !important; }
#MainMenu { display: none !important; }

/* ── Main container ── */
.block-container {
    max-width: 740px !important;
    padding: 0.5rem 1.1rem 4rem 1.1rem !important;
}

/* ── Typography scale: dark forest green headings by default ── */
h1, h2, h3, h4, h5, h6,
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6,
[data-testid="stMarkdownContainer"] h1,
[data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3,
[data-testid="stMarkdownContainer"] h4,
[data-testid="stMarkdownContainer"] h5,
[data-testid="stMarkdownContainer"] h6,
[data-testid="stHeadingWithActionElements"] h1,
[data-testid="stHeadingWithActionElements"] h2,
[data-testid="stHeadingWithActionElements"] h3 {
    font-family: 'Inter', 'Noto Sans Kannada', sans-serif !important;
    color: var(--forest-green-dark) !important;
    letter-spacing: -0.01em;
}

/* ── Headings and text inside white cards and containers must be dark and clearly readable ── */
div[style*="background: #FFFFFF"] h1,
div[style*="background: #FFFFFF"] h2,
div[style*="background: #FFFFFF"] h3,
div[style*="background: #FFFFFF"] h4,
div[style*="background:#FFFFFF"] h1,
div[style*="background:#FFFFFF"] h2,
div[style*="background:#FFFFFF"] h3,
div[style*="background:#FFFFFF"] h4,
div[style*="background: #ffffff"] h1,
div[style*="background: #ffffff"] h2,
div[style*="background: #ffffff"] h3,
div[style*="background: #ffffff"] h4,
div[style*="background: var(--card-white)"] h1,
div[style*="background: var(--card-white)"] h2,
div[style*="background: var(--card-white)"] h3,
div[style*="background-color: var(--card-white)"] h1,
div[style*="background-color: var(--card-white)"] h2,
div[style*="background-color: var(--card-white)"] h3,
.stExpander h1, .stExpander h2, .stExpander h3,
[data-testid="stExpander"] h1, [data-testid="stExpander"] h2, [data-testid="stExpander"] h3 {
    color: var(--forest-green-dark) !important;
}

/* ── Paragraph and label base styling with high contrast ── */
p, li, label,
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li {
    font-family: 'Inter', 'Noto Sans Kannada', sans-serif !important;
    color: var(--text-primary);
}

span:not([data-testid="stIconMaterial"]):not([class*="material"]),
div:not([data-testid="stIconMaterial"]):not([class*="material"]) {
    font-family: 'Inter', 'Noto Sans Kannada', sans-serif;
}

/* ── Header titles on dark green backgrounds must stay pure white ── */
.dark-header-card,
.dark-header-card h1,
.dark-header-card h2,
.dark-header-card h3,
.dark-header-card p,
.dark-header-card div,
.dark-header-card span,
.dark-header-card [data-testid="stMarkdownContainer"] h1,
.dark-header-card [data-testid="stMarkdownContainer"] h2,
.dark-header-card [data-testid="stMarkdownContainer"] h3,
.dark-header-card [data-testid="stMarkdownContainer"] p,
.dark-header-card [data-testid="stMarkdownContainer"] span {
    color: #FFFFFF !important;
}

/* ── Language bar: sticky at top ── */
div[data-testid="stRadio"]:first-of-type {
    position: sticky;
    top: 0;
    z-index: 100;
    background: var(--warm-white);
    padding: 0.5rem 0 0.4rem 0;
    border-bottom: 1px solid var(--border-light);
    margin-bottom: 0.6rem !important;
}

div[data-testid="stRadio"] > div {
    gap: 0.45rem !important;
    flex-wrap: wrap !important;
}

div[data-testid="stRadio"] label {
    font-size: 0.93rem !important;
    padding: 0.45rem 1.1rem !important;
    border-radius: 100px !important;
    border: 2px solid var(--border-mid) !important;
    background: var(--card-white) !important;
    transition: var(--transition) !important;
    font-weight: 600 !important;
    color: var(--text-secondary) !important;
    cursor: pointer;
    box-shadow: var(--shadow-xs) !important;
}

div[data-testid="stRadio"] label:hover {
    border-color: var(--sage-green) !important;
    background: var(--sage-ultra-pale) !important;
}

div[data-testid="stRadio"] label[data-checked="true"],
div[data-testid="stRadio"] label:has(input:checked) {
    background: var(--forest-green) !important;
    color: #FFFFFF !important;
    border-color: var(--forest-green) !important;
    box-shadow: 0 2px 8px rgba(42,92,42,0.3) !important;
}

/* Radio label text in Streamlit */
div[data-testid="stRadio"] label p {
    font-size: inherit !important;
    font-weight: inherit !important;
    color: inherit !important;
    margin: 0 !important;
}

/* ── Selectbox styling ── */
div[data-testid="stSelectbox"] {
    margin-bottom: 0.6rem !important;
}

/* Dropdown box container */
div[data-testid="stSelectbox"] > div > div,
div[data-testid="stSelectbox"] [data-testid="stSelectbox"] > div {
    border-radius: var(--radius-md) !important;
    border: 2px solid var(--border-light) !important;
    background: var(--card-white) !important;
    min-height: 50px !important;
    font-size: 1rem !important;
    transition: var(--transition) !important;
    box-shadow: var(--shadow-xs) !important;
}

/* Dropdown focus border */
div[data-testid="stSelectbox"] > div > div:focus-within,
div[data-testid="stSelectbox"] [data-focus-within] {
    border-color: #245B32 !important;
    box-shadow: 0 0 0 3px rgba(36,91,50,0.15) !important;
}

/* Dropdown label */
div[data-testid="stSelectbox"] label {
    font-weight: 600 !important;
    color: var(--text-secondary) !important;
    font-size: 0.88rem !important;
    margin-bottom: 0.25rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.04em !important;
}

/* ── Selected value text inside closed selectbox ── */
/* Streamlit 1.40+ / 1.66 renders selected values inside an <input> (React-Aria combobox) */
div[data-testid="stSelectbox"] input,
div[data-testid="stSelectbox"] input.react-aria-Input,
div[data-testid="stSelectbox"] input[type="text"] {
    color: #245B32 !important;
    -webkit-text-fill-color: #245B32 !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    font-family: 'Inter', 'Noto Sans Kannada', sans-serif !important;
    background: transparent !important;
}

/* Support for BaseWeb / wrapper structures if present */
div[data-testid="stSelectbox"] div[data-baseweb="select"] > div,
div[data-testid="stSelectbox"] div[data-baseweb="select"] span,
div[data-testid="stSelectbox"] div[data-baseweb="select"] div,
div[data-testid="stSelectbox"] [data-testid="stMarkdownContainer"] p,
div[data-testid="stSelectbox"] [data-testid="stSelectboxItem"] {
    color: #245B32 !important;
    -webkit-text-fill-color: #245B32 !important;
    font-weight: 600 !important;
    font-family: 'Inter', 'Noto Sans Kannada', sans-serif !important;
}

/* Placeholder text (before any selection) */
div[data-testid="stSelectbox"] input::placeholder,
div[data-testid="stSelectbox"] [data-testid="stSelectboxPlaceholder"],
div[data-testid="stSelectbox"] div[data-baseweb="select"] input::placeholder {
    color: #4A5D4A !important;
    -webkit-text-fill-color: #4A5D4A !important;
    font-weight: 400 !important;
    opacity: 1 !important;
}

/* Caret / arrow icon */
div[data-testid="stSelectbox"] button svg,
div[data-testid="stSelectbox"] svg {
    fill: #245B32 !important;
    color: #245B32 !important;
}

/* ── Dropdown open menu (Floating popover) ── */
/* Popover container */
[data-testid="stSelectboxVirtualDropdown"],
div[data-testid="stSelectboxVirtualDropdown"],
ul[data-testid="stSelectboxVirtualDropdown"],
div.react-aria-Popover[data-testid="stSelectboxVirtualDropdown"],
div[data-baseweb="popover"],
div[data-baseweb="menu"] {
    background-color: var(--card-white) !important;
    border: 1.5px solid var(--border-mid) !important;
    border-radius: var(--radius-md) !important;
    box-shadow: var(--shadow-md) !important;
    padding: 6px !important;
    z-index: 999999 !important;
}

/* List container */
[data-testid="stSelectboxVirtualDropdown"] [role="listbox"],
[data-testid="stSelectboxVirtualDropdown"] .react-aria-ListBox,
[data-testid="stSelectboxVirtualDropdown"] ul {
    background-color: var(--card-white) !important;
    padding: 0 !important;
}

/* Individual option items */
[data-testid="stSelectboxVirtualDropdown"] [role="option"],
[data-testid="stSelectboxVirtualDropdown"] .react-aria-ListBoxItem,
[data-testid="stSelectboxVirtualDropdown"] li,
div[data-baseweb="popover"] li,
div[data-baseweb="menu"] li {
    background-color: var(--card-white) !important;
    color: #182818 !important;
    font-size: 0.96rem !important;
    font-family: 'Inter', 'Noto Sans Kannada', sans-serif !important;
    padding: 0.55rem 0.85rem !important;
    margin: 2px 0 !important;
    border-radius: var(--radius-sm) !important;
    cursor: pointer !important;
    transition: var(--transition) !important;
}

/* Option text content */
[data-testid="stSelectboxVirtualDropdown"] [role="option"] *,
[data-testid="stSelectboxVirtualDropdown"] .react-aria-ListBoxItem *,
[data-testid="stSelectboxVirtualDropdown"] [data-item-hl],
div[data-baseweb="popover"] li *,
div[data-baseweb="menu"] li * {
    color: #182818 !important;
    -webkit-text-fill-color: #182818 !important;
    font-family: 'Inter', 'Noto Sans Kannada', sans-serif !important;
}

/* Hovered / Focused option */
[data-testid="stSelectboxVirtualDropdown"] [role="option"]:hover,
[data-testid="stSelectboxVirtualDropdown"] [role="option"][data-hovered="true"],
[data-testid="stSelectboxVirtualDropdown"] [role="option"][data-focused="true"],
[data-testid="stSelectboxVirtualDropdown"] .react-aria-ListBoxItem[data-hovered],
[data-testid="stSelectboxVirtualDropdown"] .react-aria-ListBoxItem[data-focused],
[data-testid="stSelectboxVirtualDropdown"] li:hover,
div[data-baseweb="popover"] li:hover {
    background-color: var(--sage-ultra-pale) !important;
}

[data-testid="stSelectboxVirtualDropdown"] [role="option"]:hover *,
[data-testid="stSelectboxVirtualDropdown"] [role="option"][data-hovered="true"] *,
[data-testid="stSelectboxVirtualDropdown"] [role="option"][data-focused="true"] *,
[data-testid="stSelectboxVirtualDropdown"] [role="option"]:hover [data-item-hl],
[data-testid="stSelectboxVirtualDropdown"] [role="option"][data-hovered="true"] [data-item-hl],
[data-testid="stSelectboxVirtualDropdown"] [role="option"][data-focused="true"] [data-item-hl],
div[data-baseweb="popover"] li:hover * {
    color: #245B32 !important;
    -webkit-text-fill-color: #245B32 !important;
    background-color: transparent !important;
}

/* Currently selected option in the open dropdown */
[data-testid="stSelectboxVirtualDropdown"] [role="option"][data-selected="true"],
[data-testid="stSelectboxVirtualDropdown"] [role="option"][aria-selected="true"],
[data-testid="stSelectboxVirtualDropdown"] .react-aria-ListBoxItem[data-selected="true"],
[data-testid="stSelectboxVirtualDropdown"] li[aria-selected="true"],
div[data-baseweb="popover"] li[aria-selected="true"] {
    background-color: #EBF3E6 !important;
    font-weight: 700 !important;
}

[data-testid="stSelectboxVirtualDropdown"] [role="option"][data-selected="true"] *,
[data-testid="stSelectboxVirtualDropdown"] [role="option"][aria-selected="true"] *,
[data-testid="stSelectboxVirtualDropdown"] [role="option"][data-selected="true"] [data-item-hl],
[data-testid="stSelectboxVirtualDropdown"] [role="option"][aria-selected="true"] [data-item-hl],
div[data-baseweb="popover"] li[aria-selected="true"] * {
    color: #245B32 !important;
    -webkit-text-fill-color: #245B32 !important;
    font-weight: 700 !important;
    background-color: transparent !important;
}

/* ── Stacked radio (priority, season, irrigation) ── */
div[data-testid="stRadio"] > label {
    font-weight: 600 !important;
    color: var(--text-secondary) !important;
    font-size: 0.88rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.04em !important;
    margin-bottom: 0.3rem !important;
}

/* ── Action Buttons (scoped specifically to st.button elements) ── */
div[data-testid="stButton"] > button,
div[data-testid="stButton"] > button[kind="primary"],
div[data-testid="stButton"] > button[kind="secondary"],
.stButton > button,
.stButton > button[kind="primary"],
.stButton > button[kind="secondary"] {
    background: #286332 !important;
    background-color: #286332 !important;
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    border: 1.5px solid #6B8F5E !important;
    border-radius: var(--radius-md) !important;
    padding: 0.8rem 2.0rem !important;
    font-size: 1.05rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.02em !important;
    box-shadow: 0 4px 14px rgba(40,99,50,0.22) !important;
    transition: var(--transition) !important;
    min-height: 50px !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    text-align: center !important;
    cursor: pointer !important;
    box-sizing: border-box !important;
}

/* Ensure inner <p> and <span> inside buttons inherit crisp white text and center alignment */
div[data-testid="stButton"] > button p,
div[data-testid="stButton"] > button span,
div[data-testid="stButton"] > button [data-testid="stMarkdownContainer"] p,
.stButton > button p,
.stButton > button span,
.stButton > button [data-testid="stMarkdownContainer"] p {
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    background: transparent !important;
    background-color: transparent !important;
    box-shadow: none !important;
    border: none !important;
    padding: 0 !important;
    margin: 0 !important;
    font-size: inherit !important;
    font-weight: 700 !important;
    font-family: 'Inter', 'Noto Sans Kannada', sans-serif !important;
    display: inline-block !important;
    text-align: center !important;
}

/* Hover state: lighter green background with crisp white text */
div[data-testid="stButton"] > button:hover,
div[data-testid="stButton"] > button[kind="primary"]:hover,
div[data-testid="stButton"] > button[kind="secondary"]:hover,
.stButton > button:hover,
.stButton > button[kind="primary"]:hover,
.stButton > button[kind="secondary"]:hover {
    background: #337B3E !important;
    background-color: #337B3E !important;
    border-color: #8FA897 !important;
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    box-shadow: 0 6px 20px rgba(40,99,50,0.32) !important;
    transform: translateY(-1px) !important;
}

div[data-testid="stButton"] > button:hover p,
div[data-testid="stButton"] > button:hover span,
div[data-testid="stButton"] > button:hover [data-testid="stMarkdownContainer"] p,
.stButton > button:hover p,
.stButton > button:hover span,
.stButton > button:hover [data-testid="stMarkdownContainer"] p {
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    background: transparent !important;
    background-color: transparent !important;
}

/* Focus state: clear, accessible green focus ring */
div[data-testid="stButton"] > button:focus,
div[data-testid="stButton"] > button:focus-visible,
.stButton > button:focus,
.stButton > button:focus-visible {
    outline: none !important;
    border-color: #9BBD8D !important;
    box-shadow: 0 0 0 3px rgba(107, 143, 94, 0.5), 0 4px 14px rgba(40,99,50,0.25) !important;
}

/* Active / pressed state */
div[data-testid="stButton"] > button:active,
.stButton > button:active {
    transform: translateY(0) !important;
    background: #1E4D27 !important;
    background-color: #1E4D27 !important;
    box-shadow: 0 2px 8px rgba(40,99,50,0.3) !important;
}

/* ── Strategy Expanders & General Expander Styling ── */
.stExpander details,
[data-testid="stExpander"] details {
    border: 1.5px solid var(--border-light) !important;
    border-radius: var(--radius-md) !important;
    background: var(--card-white) !important;
    margin-bottom: 0.75rem !important;
    box-shadow: var(--shadow-xs) !important;
    transition: var(--transition) !important;
    overflow: hidden !important;
}

.stExpander details:hover,
[data-testid="stExpander"] details:hover {
    border-color: var(--border-mid) !important;
    box-shadow: var(--shadow-sm) !important;
}

.stExpander details[open],
[data-testid="stExpander"] details[open] {
    border-color: var(--sage-green) !important;
    box-shadow: var(--shadow-sm) !important;
}

/* Suppress broken Material icon ligature text in expander headers */
[data-testid="stExpander"] summary span[data-testid="stIconMaterial"],
details summary span[data-testid="stIconMaterial"] {
    display: none !important;
    width: 0 !important;
    height: 0 !important;
    overflow: hidden !important;
    visibility: hidden !important;
    font-size: 0 !important;
    line-height: 0 !important;
}

/* Expander Header (Summary) */
[data-testid="stExpander"] details > summary,
[data-testid="stExpander"] summary,
details > summary,
.streamlit-expanderHeader {
    display: flex !important;
    flex-direction: row !important;
    align-items: center !important;
    justify-content: flex-start !important;
    background: var(--card-white) !important;
    font-weight: 600 !important;
    font-size: 0.96rem !important;
    padding: 0.95rem 1.25rem !important;
    color: var(--text-primary) !important;
    cursor: pointer !important;
    user-select: none !important;
    border: none !important;
    outline: none !important;
    min-height: 52px !important;
    box-sizing: border-box !important;
    gap: 0.5rem !important;
    transition: background 0.15s ease !important;
}

/* Clean CSS-drawn chevron arrow indicator */
details[data-testid="stExpander"] > summary::before,
.stExpander details > summary::before,
details > summary::before {
    content: "" !important;
    display: inline-block !important;
    width: 8px !important;
    height: 8px !important;
    min-width: 8px !important;
    min-height: 8px !important;
    border-right: 2.5px solid var(--forest-green) !important;
    border-bottom: 2.5px solid var(--forest-green) !important;
    transform: rotate(-45deg) !important;
    transition: transform 0.22s cubic-bezier(0.4, 0, 0.2, 1) !important;
    margin-right: 0.4rem !important;
    margin-left: 0.1rem !important;
    flex-shrink: 0 !important;
}

/* Rotate chevron downward when expander is open */
details[data-testid="stExpander"][open] > summary::before,
.stExpander details[open] > summary::before,
details[open] > summary::before {
    transform: rotate(45deg) !important;
}

[data-testid="stExpander"] details > summary:hover,
[data-testid="stExpander"] summary:hover,
details > summary:hover {
    background: var(--sage-ultra-pale) !important;
}

/* Header title text container - prevent overlap & ensure alignment */
[data-testid="stExpander"] summary [data-testid="stMarkdownContainer"],
[data-testid="stExpander"] summary p,
details > summary [data-testid="stMarkdownContainer"],
details > summary p {
    font-size: 0.96rem !important;
    font-weight: 600 !important;
    color: var(--text-primary) !important;
    line-height: 1.4 !important;
    margin: 0 !important;
    padding: 0 !important;
    display: inline-block !important;
    word-break: break-word !important;
    flex: 1 1 auto !important;
}

/* Expander Details (Opened Content) */
[data-testid="stExpanderDetails"],
details > div {
    padding: 1.15rem 1.35rem !important;
    border-top: 1px solid var(--border-light) !important;
    background: #FCFBF9 !important;
}

[data-testid="stExpanderDetails"] p,
[data-testid="stExpanderDetails"] li {
    font-size: 0.9rem !important;
    line-height: 1.55 !important;
    color: var(--text-primary) !important;
    margin-bottom: 0.35rem !important;
}

[data-testid="stExpanderDetails"] strong {
    color: var(--forest-green) !important;
    font-weight: 700 !important;
}

[data-testid="stExpanderDetails"] ul {
    margin-top: 0.2rem !important;
    margin-bottom: 0.6rem !important;
    padding-left: 1.2rem !important;
}

/* ── Streamlit alert boxes ── */
div[data-testid="stAlert"] {
    border-radius: var(--radius-md) !important;
    font-size: 0.91rem !important;
    padding: 0.9rem 1.1rem !important;
}

/* ── Divider ── */
hr {
    border: none !important;
    border-top: 1.5px solid var(--border-light) !important;
    margin: 1.8rem 0 !important;
}

/* ── Caption ── */
.stCaption, [data-testid="stCaptionContainer"] {
    color: var(--text-muted) !important;
    font-size: 0.8rem !important;
    line-height: 1.6 !important;
}

/* ── Tooltip/helper text in forms ── */
small, .stTextInput .instructions {
    color: var(--text-light) !important;
    font-size: 0.78rem !important;
}

/* ── Mobile responsive ── */
@media (max-width: 768px) {
    .block-container {
        padding: 0.25rem 0.65rem 3rem 0.65rem !important;
    }

    h1 { font-size: 1.55rem !important; }
    h2 { font-size: 1.25rem !important; }
    h3 { font-size: 1.1rem !important; }

    div[data-testid="stSelectbox"] > div > div {
        min-height: 54px !important;
        font-size: 1.05rem !important;
    }

    div[data-testid="stSelectbox"] input,
    div[data-testid="stSelectbox"] input.react-aria-Input,
    div[data-testid="stSelectbox"] div[data-baseweb="select"] span {
        font-size: 1.05rem !important;
        color: #245B32 !important;
        -webkit-text-fill-color: #245B32 !important;
    }

    div[data-testid="stButton"] > button,
    .stButton > button {
        min-height: 52px !important;
        font-size: 1.08rem !important;
    }

    [data-testid="stExpander"] details > summary,
    [data-testid="stExpander"] summary,
    details > summary {
        padding: 0.85rem 1rem !important;
        font-size: 0.92rem !important;
        min-height: 48px !important;
    }
}

@media (max-width: 480px) {
    .block-container {
        padding: 0.1rem 0.5rem 2rem 0.5rem !important;
    }
    div[data-testid="stButton"] > button,
    .stButton > button {
        min-height: 54px !important;
        font-size: 1.1rem !important;
        border-radius: 12px !important;
    }
}
</style>
""", unsafe_allow_html=True)

# =====================================================================
# TRANSLATIONS
# =====================================================================
T = {
    "title": ("Field Shift: crop rotation helper", "ಫೀಲ್ಡ್ ಶಿಫ್ಟ್: ಬೆಳೆ ಪರ್ಯಾಯ ಸಹಾಯಕ"),
    "language": ("Language", "ಭಾಷೆ"),
    "details": ("Your details", "ನಿಮ್ಮ ವಿವರಗಳು"),
    "taluk": ("Taluk", "ತಾಲೂಕು"),
    "soil": ("Soil", "ಮಣ್ಣು"),
    "season": ("Season you are planning", "ನೀವು ಯೋಜಿಸುತ್ತಿರುವ ಋತು"),
    "last": ("Last crop", "ಹಿಂದಿನ ಬೆಳೆ"),
    "prev": ("Crop before that (optional)", "ಅದಕ್ಕೂ ಮೊದಲಿನ ಬೆಳೆ (ಐಚ್ಛಿಕ)"),
    "irr": ("Do you have irrigation?", "ನೀರಾವರಿ ಇದೆಯೇ?"),
    "pri": ("What matters most?", "ಯಾವುದು ಮುಖ್ಯ?"),
    "go": ("Get suggestion", "ಸಲಹೆ ಪಡೆಯಿರಿ"),
    "best": ("Best choices for you", "ನಿಮಗೆ ಉತ್ತಮ ಆಯ್ಕೆಗಳು"),
    "score": ("Score", "ಅಂಕ"),
    "rotation": ("Crop rotation", "ಬೆಳೆ ಪರ್ಯಾಯ"),
    "soilw": ("Soil", "ಮಣ್ಣು"),
    "climate": ("Weather and climate", "ಹವಾಮಾನ"),
    "water": ("Water use", "ನೀರಿನ ಬಳಕೆ"),
    "warning": ("Warning", "ಎಚ್ಚರಿಕೆ"),
    "equal": ("Equal choice", "ಸಮಾನ ಆಯ್ಕೆ"),
    "place": ("Place", "ಸ್ಥಾನ"),
    "yes": ("I have irrigation", "ನೀರಾವರಿ ಇದೆ"),
    "no": ("I do not", "ಇಲ್ಲ"),
    "disclaimer": (
        "This is guidance based on NASA weather data and published research. It is not a guarantee. Please check with your agriculture office.",
        "ಇದು ನಾಸಾ ಹವಾಮಾನ ಮಾಹಿತಿ ಮತ್ತು ಪ್ರಕಟಿತ ಸಂಶೋಧನೆಯ ಆಧಾರದ ಮಾರ್ಗದರ್ಶನ. ಇದು ಖಾತರಿ ಅಲ್ಲ. ದಯವಿಟ್ಟು ನಿಮ್ಮ ಕೃಷಿ ಕಚೇರಿಯಲ್ಲಿ ಪರಿಶೀಲಿಸಿ."),
    # New keys for redesigned sections
    "hero_subtitle": (
        "Smart crop rotation advice powered by NASA climate data, local soil research and your priorities.",
        "ನಾಸಾ ಹವಾಮಾನ ಮಾಹಿತಿ, ಸ್ಥಳೀಯ ಮಣ್ಣಿನ ಸಂಶೋಧನೆ ಮತ್ತು ನಿಮ್ಮ ಆದ್ಯತೆಗಳ ಆಧಾರದಲ್ಲಿ ಬೆಳೆ ಪರ್ಯಾಯ ಸಲಹೆ.",
    ),
    "start_btn": ("Start Recommendation", "ಶಿಫಾರಸು ಪ್ರಾರಂಭಿಸಿ"),
    "how_title": ("How it works", "ಇದು ಹೇಗೆ ಕೆಲಸ ಮಾಡುತ್ತದೆ"),
    "how_1": ("You share your field details", "ನಿಮ್ಮ ಹೊಲದ ವಿವರಗಳನ್ನು ಹಂಚಿಕೊಳ್ಳಿ"),
    "how_2": ("We analyse NASA climate data and research", "ನಾಸಾ ಹವಾಮಾನ ಮಾಹಿತಿ ಮತ್ತು ಸಂಶೋಧನೆಯನ್ನು ವಿಶ್ಲೇಷಿಸುತ್ತೇವೆ"),
    "how_3": ("You get scored crop suggestions", "ಅಂಕ ನೀಡಿದ ಬೆಳೆ ಸಲಹೆಗಳನ್ನು ಪಡೆಯಿರಿ"),
    "benefits_title": ("Benefits for farmers", "ರೈತರಿಗೆ ಪ್ರಯೋಜನಗಳು"),
    "ben_1": ("Improve soil health through smart rotation", "ಬುದ್ಧಿವಂತ ಪರ್ಯಾಯದ ಮೂಲಕ ಮಣ್ಣಿನ ಆರೋಗ್ಯ ಸುಧಾರಿಸಿ"),
    "ben_2": ("Save water with the right crop choice", "ಸರಿಯಾದ ಬೆಳೆ ಆಯ್ಕೆಯಿಂದ ನೀರು ಉಳಿಸಿ"),
    "ben_3": ("Reduce harvest risk using climate data", "ಹವಾಮಾನ ಮಾಹಿತಿ ಬಳಸಿ ಫಸಲು ಅಪಾಯ ಕಡಿಮೆ ಮಾಡಿ"),
    "ben_4": ("Evidence-based decisions backed by research", "ಸಂಶೋಧನೆಯ ಆಧಾರದ ನಿರ್ಧಾರಗಳು"),
    "nasa_title": ("Powered by NASA data", "ನಾಸಾ ಮಾಹಿತಿಯಿಂದ ಚಾಲಿತ"),
    "nasa_desc": (
        "Field Shift uses NASA POWER climate data (a model estimate) spanning 1981-2025 — including rainfall patterns, dry spell risks and soil moisture estimates — combined with published agricultural research from the University of Agricultural Sciences, Dharwad and ICAR to provide evidence-based crop rotation advice for Belagavi district.",
        "ಫೀಲ್ಡ್ ಶಿಫ್ಟ್ 1981-2025ರ ನಾಸಾ POWER ಹವಾಮಾನ ಮಾಹಿತಿಯನ್ನು (ಮಾದರಿ ಅಂದಾಜು) — ಮಳೆ ಮಾದರಿಗಳು, ಒಣ ಅವಧಿಯ ಅಪಾಯಗಳು ಮತ್ತು ಮಣ್ಣಿನ ತೇವಾಂಶ ಅಂದಾಜುಗಳನ್ನು — ಧಾರವಾಡದ ಕೃಷಿ ವಿಶ್ವವಿದ್ಯಾಲಯ ಮತ್ತು ಐಸಿಎಆರ್‌ನ ಪ್ರಕಟಿತ ಕೃಷಿ ಸಂಶೋಧನೆಯೊಂದಿಗೆ ಸಂಯೋಜಿಸಿ ಬೆಳಗಾವಿ ಜಿಲ್ಲೆಗೆ ಆಧಾರಿತ ಬೆಳೆ ಪರ್ಯಾಯ ಸಲಹೆ ನೀಡುತ್ತದೆ.",
    ),
    "form_location": ("Location & Soil", "ಸ್ಥಳ ಮತ್ತು ಮಣ್ಣು"),
    "form_crop_history": ("Crop History", "ಬೆಳೆ ಇತಿಹಾಸ"),
    "form_preferences": ("Your Preferences", "ನಿಮ್ಮ ಆದ್ಯತೆಗಳು"),
    "form_season_crop": ("Season & Comparison", "ಋತು ಮತ್ತು ಹೋಲಿಕೆ"),
    "usual_crop": (
        "Your usual crop for this season (for comparison)",
        "ಈ ಋತುವಿನಲ್ಲಿ ನೀವು ಸಾಮಾನ್ಯವಾಗಿ ಬೆಳೆಯುವ ಬೆಳೆ (ಹೋಲಿಕೆಗಾಗಿ)",
    ),
    "results_title": ("Your Recommendations", "ನಿಮ್ಮ ಶಿಫಾರಸುಗಳು"),
    "score_breakdown": ("Score Breakdown", "ಅಂಕಗಳ ವಿವರ"),
    "strategies_title": ("Compare 3 strategies", "3 ತಂತ್ರಗಳನ್ನು ಹೋಲಿಸಿ"),
    "strategies_note": ("", ""),
    "why_suggested": ("Why suggested", "ಏಕೆ ಶಿಫಾರಸು ಮಾಡಲಾಗಿದೆ"),
    "evidence": ("Evidence", "ಸಾಕ್ಷ್ಯ"),
    "benefits": ("Benefits", "ಪ್ರಯೋಜನಗಳು"),
    "info_gaps": ("Information gaps", "ಮಾಹಿತಿ ಕೊರತೆಗಳು"),
    "risks": ("Risks", "ಅಪಾಯಗಳು"),
    "assumption_title": ("If our water assumption is wrong", "ನಮ್ಮ ನೀರಿನ ಊಹೆ ತಪ್ಪಾಗಿದ್ದರೆ"),
    "back_to_top": ("New recommendation", "ಹೊಸ ಶಿಫಾರಸು"),
}

from scoring import ZONE_FACTS, TALUK_KN, SOIL_KN, PRIORITY, SEASON


# =====================================================================
# HELPER: Language setup
# =====================================================================
def setup_language():
    """Returns (lang_code, index, translator_fn)."""
    if "lang_version" not in st.session_state:
        st.session_state["lang_version"] = 0
    if "current_lang" not in st.session_state:
        q_lang = st.query_params.get("lang")
        st.session_state["current_lang"] = q_lang if q_lang in ("kn", "en") else "kn"

    choice = st.radio(
        "Language / ಭಾಷೆ",
        ["ಕನ್ನಡ", "English"],
        index=0 if st.session_state["current_lang"] == "kn" else 1,
        horizontal=True,
        key="lang_choice",
    )
    new_lang = "kn" if choice == "ಕನ್ನಡ" else "en"

    # Immediately detect language switch, increment version, copy state, and rerun
    if new_lang != st.session_state["current_lang"]:
        old_v = st.session_state["lang_version"]
        new_v = old_v + 1
        st.session_state["lang_version"] = new_v
        st.session_state["current_lang"] = new_lang

        widget_prefixes = [
            "taluk_input",
            "soil_input",
            "season_input",
            "last_crop_input",
            "prev_crop_input",
            "irrigation_input",
            "priority_input",
            "usual_crop_input",
        ]
        for pfx in widget_prefixes:
            old_k = f"{pfx}_{old_v}"
            new_k = f"{pfx}_{new_v}"
            if old_k in st.session_state:
                st.session_state[new_k] = st.session_state[old_k]

        st.rerun()

    lang = st.session_state["current_lang"]
    idx = 0 if lang == "en" else 1

    def t(k):
        return T[k][idx]

    return lang, idx, t


# =====================================================================
# HELPER: HTML cleaner & Score bar HTML
# =====================================================================
def clean_html(html_str):
    """Strip HTML comments and leading indentation so markdown never parses HTML as code blocks."""
    cleaned = re.sub(r"<!--.*?-->", "", html_str, flags=re.DOTALL)
    lines = [line.strip() for line in cleaned.splitlines() if line.strip()]
    return "\n".join(lines)


def score_bar_html(score, max_score, label, detail):
    """Render a horizontal score bar as HTML."""
    pct = int((score / max_score) * 100) if max_score > 0 else 0
    # Color based on percentage
    if pct >= 75:
        bar_color = "#2A5C2A"
        bar_bg = "rgba(42,92,42,0.12)"
        score_color = "#2A5C2A"
    elif pct >= 50:
        bar_color = "#6B8F5E"
        bar_bg = "rgba(107,143,94,0.12)"
        score_color = "#4A6E3D"
    elif pct >= 25:
        bar_color = "#B8880A"
        bar_bg = "rgba(184,136,10,0.10)"
        score_color = "#8A6300"
    else:
        bar_color = "#A83820"
        bar_bg = "rgba(168,56,32,0.10)"
        score_color = "#A83820"

    return clean_html(f"""
<div style="margin-bottom: 13px;">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">
<span style="font-weight: 600; font-size: 0.84rem; color: #182818; font-family: 'Inter', 'Noto Sans Kannada', sans-serif; letter-spacing: 0.01em;">{label}</span>
<span style="font-size: 0.82rem; color: {score_color}; font-weight: 700; font-family: 'Inter', sans-serif; background: {bar_bg}; padding: 1px 7px; border-radius: 20px; white-space: nowrap;">{score}/{max_score}</span>
</div>
<div style="background: #EAF0E5; border-radius: 100px; height: 7px; overflow: hidden; margin-bottom: 5px;">
<div style="width: {pct}%; height: 100%; background: linear-gradient(90deg, {bar_color}CC, {bar_color}); border-radius: 100px;"></div>
</div>
<div style="font-size: 0.77rem; color: #62786A; line-height: 1.45; font-family: 'Inter', 'Noto Sans Kannada', sans-serif; padding-left: 1px;">{detail}</div>
</div>
""")


# =====================================================================
# HELPER: Crop card HTML
# =====================================================================
def render_crop_card(x, lang, t_fn, is_top=False):
    """Render a recommendation card for a crop."""
    badge_text = t_fn("equal") if x["tied"] else f"{t_fn('place')} {x['place']}"
    crop_name = sc.crop_word(lang, x["crop"])
    total = x["total"]
    max_total = x["max_total"]
    pct = int((total / max_total) * 100) if max_total > 0 else 0

    # Badge & border colors
    if x["place"] == 1:
        badge_bg = "#2A5C2A"
        badge_fg = "#FFFFFF"
        border_color = "#2A5C2A"
        card_accent = "linear-gradient(180deg, rgba(42,92,42,0.06) 0%, transparent 50%)"
    elif x["place"] == 2:
        badge_bg = "#6B8F5E"
        badge_fg = "#FFFFFF"
        border_color = "#6B8F5E"
        card_accent = "linear-gradient(180deg, rgba(107,143,94,0.05) 0%, transparent 50%)"
    else:
        badge_bg = "#9BBD8D"
        badge_fg = "#182818"
        border_color = "#9BBD8D"
        card_accent = "linear-gradient(180deg, rgba(155,189,141,0.04) 0%, transparent 50%)"

    if x["tied"]:
        badge_bg = "#C49A00"
        badge_fg = "#FFFFFF"
        border_color = "#C49A00"
        card_accent = "linear-gradient(180deg, rgba(196,154,0,0.05) 0%, transparent 50%)"

    # Score ring color
    if pct >= 75:
        ring_color = "#2A5C2A"
        ring_track = "rgba(42,92,42,0.15)"
    elif pct >= 50:
        ring_color = "#6B8F5E"
        ring_track = "rgba(107,143,94,0.15)"
    else:
        ring_color = "#B8880A"
        ring_track = "rgba(184,136,10,0.12)"

    left_border = f"border-left: 5px solid {border_color};" if is_top else f"border-left: 3px solid {border_color};"
    top_shadow = "0 6px 20px rgba(0,0,0,0.10), 0 2px 6px rgba(0,0,0,0.06)" if is_top else "0 2px 8px rgba(0,0,0,0.07), 0 1px 3px rgba(0,0,0,0.04)"

    parts = x["parts"]
    rot = parts["rotation"]
    soil = parts["soil"]
    clim = parts["climate"]
    wat = parts["water_use"]

    bars_html = ""
    bars_html += score_bar_html(rot[0], sc.MAX_PART_POINTS["rotation"], t_fn("rotation"), rot[1])
    bars_html += score_bar_html(soil[0], sc.MAX_PART_POINTS["soil"], t_fn("soilw"), soil[1])
    bars_html += score_bar_html(clim[0], sc.MAX_PART_POINTS["climate"], t_fn("climate"), clim[1])
    bars_html += score_bar_html(wat[0], sc.MAX_PART_POINTS["water_use"], t_fn("water"), wat[1])

    card_html = clean_html(f"""
<div style="background: #FFFFFF; background-image: {card_accent}; border-radius: 16px; {left_border} box-shadow: {top_shadow}; padding: 1.3rem 1.2rem 1.1rem 1.2rem; margin-bottom: 1rem; font-family: 'Inter', 'Noto Sans Kannada', sans-serif; transition: box-shadow 0.22s ease;">
<div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem; flex-wrap: wrap; gap: 0.5rem;">
<div style="display: flex; align-items: center; gap: 0.65rem; flex-wrap: wrap; flex: 1; min-width: 0;">
<span style="background: {badge_bg}; color: {badge_fg}; font-size: 0.72rem; font-weight: 700; padding: 0.28rem 0.75rem; border-radius: 100px; letter-spacing: 0.04em; text-transform: uppercase; white-space: nowrap; flex-shrink: 0;">{badge_text}</span>
<span style="font-size: 1.18rem; font-weight: 700; color: #182818; line-height: 1.25; word-break: break-word;">{crop_name}</span>
</div>
<div style="text-align: center; flex-shrink: 0;">
<div style="width: 56px; height: 56px; border-radius: 50%; border: 3.5px solid {ring_color}; background: {ring_track}; display: flex; align-items: center; justify-content: center; flex-direction: column;">
<span style="font-size: 1.0rem; font-weight: 800; color: {ring_color}; line-height: 1; font-family: 'Inter', sans-serif;">{total}</span>
<span style="font-size: 0.52rem; color: #62786A; line-height: 1; font-family: 'Inter', sans-serif; letter-spacing: 0.01em;">/{max_total}</span>
</div>
</div>
</div>
<div style="height: 1px; background: linear-gradient(90deg, {border_color}30, transparent); margin-bottom: 1rem; border-radius: 1px;"></div>
{bars_html}
</div>
""")
    return card_html


# =====================================================================
# SECTION: Hero / Landing
# =====================================================================
def render_hero(t_fn, lang):
    """Render the landing hero section."""
    # Top brand bar
    st.markdown(clean_html(f"""
    <div class="dark-header-card" style="
        background: linear-gradient(145deg, #1B3D1B 0%, #2A5C2A 45%, #3A6E3A 80%, #2A5C2A 100%);
        border-radius: 20px;
        padding: 2.4rem 1.8rem 2rem 1.8rem;
        margin-bottom: 1.4rem;
        text-align: center;
        box-shadow: 0 8px 28px rgba(27,61,27,0.28), 0 2px 8px rgba(0,0,0,0.12);
        position: relative;
        overflow: hidden;
    ">
        <div style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: radial-gradient(ellipse at 30% 20%, rgba(155,189,141,0.15) 0%, transparent 60%); pointer-events: none;"></div>
        <div style="font-size: 0.75rem; letter-spacing: 2.5px; color: #FFFFFF !important; text-transform: uppercase; margin-bottom: 0.6rem; font-family: 'Inter', sans-serif; font-weight: 700; opacity: 0.95;">
            NASA Space Apps Challenge
        </div>
        <h1 style="color: #FFFFFF !important; font-size: 2.1rem; font-weight: 800; margin: 0 0 0.6rem 0; font-family: 'Inter', 'Noto Sans Kannada', sans-serif; line-height: 1.15; letter-spacing: -0.02em;">
            {"ಫೀಲ್ಡ್ ಶಿಫ್ಟ್" if lang == "kn" else "Field Shift"}
        </h1>
        <p style="color: #FFFFFF !important; font-size: 0.95rem; margin: 0; line-height: 1.6; font-family: 'Inter', 'Noto Sans Kannada', sans-serif; max-width: 420px; margin: 0 auto; opacity: 0.95;">
            {t_fn("hero_subtitle")}
        </p>
    </div>
    """), unsafe_allow_html=True)

    # How it works
    st.markdown(clean_html(f"""
    <div style="
        background: #FFFFFF;
        border-radius: 16px;
        padding: 1.4rem 1.3rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
        border: 1.5px solid #DDE8D7;
    ">
        <h3 style="color: #2A5C2A !important; font-size: 1.0rem; font-weight: 700; margin: 0 0 1.1rem 0; font-family: 'Inter', 'Noto Sans Kannada', sans-serif; letter-spacing: -0.01em; display: flex; align-items: center; gap: 0.5rem;">
            <span style="display: inline-block; width: 4px; height: 1.1rem; background: #2A5C2A; border-radius: 2px; flex-shrink: 0;"></span>
            {t_fn("how_title")}
        </h3>
        <div style="display: flex; flex-direction: column; gap: 0.85rem;">
            <div style="display: flex; align-items: flex-start; gap: 0.9rem;">
                <div style="min-width: 34px; height: 34px; background: linear-gradient(135deg, #2A5C2A, #3A6E3A); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 800; color: #FFFFFF; font-size: 0.82rem; flex-shrink: 0; box-shadow: 0 2px 6px rgba(42,92,42,0.3);">1</div>
                <span style="font-size: 0.93rem; color: #182818; padding-top: 6px; font-family: 'Inter', 'Noto Sans Kannada', sans-serif; line-height: 1.4;">{t_fn("how_1")}</span>
            </div>
            <div style="display: flex; align-items: flex-start; gap: 0.9rem;">
                <div style="min-width: 34px; height: 34px; background: linear-gradient(135deg, #2A5C2A, #3A6E3A); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 800; color: #FFFFFF; font-size: 0.82rem; flex-shrink: 0; box-shadow: 0 2px 6px rgba(42,92,42,0.3);">2</div>
                <span style="font-size: 0.93rem; color: #182818; padding-top: 6px; font-family: 'Inter', 'Noto Sans Kannada', sans-serif; line-height: 1.4;">{t_fn("how_2")}</span>
            </div>
            <div style="display: flex; align-items: flex-start; gap: 0.9rem;">
                <div style="min-width: 34px; height: 34px; background: linear-gradient(135deg, #2A5C2A, #3A6E3A); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 800; color: #FFFFFF; font-size: 0.82rem; flex-shrink: 0; box-shadow: 0 2px 6px rgba(42,92,42,0.3);">3</div>
                <span style="font-size: 0.93rem; color: #182818; padding-top: 6px; font-family: 'Inter', 'Noto Sans Kannada', sans-serif; line-height: 1.4;">{t_fn("how_3")}</span>
            </div>
        </div>
    </div>
    """), unsafe_allow_html=True)

    # Benefits for farmers
    st.markdown(clean_html(f"""
    <div style="
        background: #FFFFFF;
        border-radius: 16px;
        padding: 1.4rem 1.3rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
        border: 1.5px solid #DDE8D7;
    ">
        <h3 style="color: #2A5C2A !important; font-size: 1.0rem; font-weight: 700; margin: 0 0 1.1rem 0; font-family: 'Inter', 'Noto Sans Kannada', sans-serif; letter-spacing: -0.01em; display: flex; align-items: center; gap: 0.5rem;">
            <span style="display: inline-block; width: 4px; height: 1.1rem; background: #2A5C2A; border-radius: 2px; flex-shrink: 0;"></span>
            {t_fn("benefits_title")}
        </h3>
        <div style="display: flex; flex-direction: column; gap: 0.72rem;">
            <div style="display: flex; align-items: flex-start; gap: 0.8rem;">
                <div style="min-width: 22px; height: 22px; background: #EBF3E6; border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0; margin-top: 1px;">
                    <div style="width: 8px; height: 8px; background: #6B8F5E; border-radius: 50%;"></div>
                </div>
                <span style="font-size: 0.91rem; color: #182818; font-family: 'Inter', 'Noto Sans Kannada', sans-serif; line-height: 1.45;">{t_fn("ben_1")}</span>
            </div>
            <div style="display: flex; align-items: flex-start; gap: 0.8rem;">
                <div style="min-width: 22px; height: 22px; background: #EBF3E6; border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0; margin-top: 1px;">
                    <div style="width: 8px; height: 8px; background: #6B8F5E; border-radius: 50%;"></div>
                </div>
                <span style="font-size: 0.91rem; color: #182818; font-family: 'Inter', 'Noto Sans Kannada', sans-serif; line-height: 1.45;">{t_fn("ben_2")}</span>
            </div>
            <div style="display: flex; align-items: flex-start; gap: 0.8rem;">
                <div style="min-width: 22px; height: 22px; background: #EBF3E6; border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0; margin-top: 1px;">
                    <div style="width: 8px; height: 8px; background: #6B8F5E; border-radius: 50%;"></div>
                </div>
                <span style="font-size: 0.91rem; color: #182818; font-family: 'Inter', 'Noto Sans Kannada', sans-serif; line-height: 1.45;">{t_fn("ben_3")}</span>
            </div>
            <div style="display: flex; align-items: flex-start; gap: 0.8rem;">
                <div style="min-width: 22px; height: 22px; background: #EBF3E6; border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0; margin-top: 1px;">
                    <div style="width: 8px; height: 8px; background: #6B8F5E; border-radius: 50%;"></div>
                </div>
                <span style="font-size: 0.91rem; color: #182818; font-family: 'Inter', 'Noto Sans Kannada', sans-serif; line-height: 1.45;">{t_fn("ben_4")}</span>
            </div>
        </div>
    </div>
    """), unsafe_allow_html=True)

    # NASA data section
    st.markdown(clean_html(f"""
    <div style="
        background: linear-gradient(135deg, #EBF3E6 0%, #F2F7EE 100%);
        border-radius: 16px;
        padding: 1.4rem 1.3rem;
        margin-bottom: 1.4rem;
        border: 1.5px solid #C8DFBC;
        box-shadow: 0 1px 4px rgba(0,0,0,0.04);
    ">
        <h3 style="color: #2A5C2A !important; font-size: 1.0rem; font-weight: 700; margin: 0 0 0.75rem 0; font-family: 'Inter', 'Noto Sans Kannada', sans-serif; letter-spacing: -0.01em; display: flex; align-items: center; gap: 0.5rem;">
            <span style="font-size: 1.1rem;">🛰️</span>
            {t_fn("nasa_title")}
        </h3>
        <p style="font-size: 0.87rem; color: #3D5240; margin: 0; line-height: 1.65; font-family: 'Inter', 'Noto Sans Kannada', sans-serif;">
            {t_fn("nasa_desc")}
        </p>
    </div>
    """), unsafe_allow_html=True)


# =====================================================================
# SECTION: Input Form
# =====================================================================
def render_form(lang, i, t_fn):
    """Render the farmer input form and return the inputs + submitted flag."""
    # Section header card
    st.markdown(clean_html(f"""
    <div class="dark-header-card" style="
        background: linear-gradient(135deg, #2A5C2A 0%, #1B3D1B 100%);
        border-radius: 16px 16px 0 0;
        padding: 1.2rem 1.4rem 1rem 1.4rem;
        box-shadow: 0 2px 8px rgba(42,92,42,0.15);
    ">
        <h2 style="color: #FFFFFF !important; font-size: 1.15rem; font-weight: 700; margin: 0; font-family: 'Inter', 'Noto Sans Kannada', sans-serif; letter-spacing: -0.01em;">
            {t_fn("details")}
        </h2>
        <p style="color: #FFFFFF !important; font-size: 0.85rem; margin: 0.3rem 0 0 0; font-family: 'Inter', 'Noto Sans Kannada', sans-serif; opacity: 0.95;">
            {"Fill in your field details to get personalised crop suggestions." if lang == "en" else "ನಿಮ್ಮ ಹೊಲದ ವಿವರಗಳನ್ನು ನಮೂದಿಸಿ ಮತ್ತು ಅನುಕೂಲಕರ ಬೆಳೆ ಸಲಹೆ ಪಡೆಯಿರಿ."}
        </p>
    </div>
    <div style="background: #FFFFFF; border-left: 1.5px solid #DDE8D7; border-right: 1.5px solid #DDE8D7; padding: 1.2rem 0 0 0; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
    </div>
    """), unsafe_allow_html=True)

    # ── Location & Soil ──
    st.markdown(f"""
    <div style="padding: 0 0 0 0;">
        <div style="display: flex; align-items: center; gap: 0.5rem; margin: 0.2rem 0 0.5rem 0;">
            <div style="width: 3px; height: 1rem; background: #2A5C2A; border-radius: 2px; flex-shrink: 0;"></div>
            <p style="font-size: 0.78rem; font-weight: 700; color: #245B32; text-transform: uppercase; letter-spacing: 1.2px; margin: 0; font-family: 'Inter', 'Noto Sans Kannada', sans-serif;">
                {t_fn("form_location")}
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    v = st.session_state.get("lang_version", 0)

    taluk = st.selectbox(
        t_fn("taluk"),
        list(sc.TALUK_TO_ZONE),
        format_func=lambda x: x if lang == "en" else TALUK_KN[x],
        key=f"taluk_input_{v}",
    )
    soil = st.selectbox(
        t_fn("soil"),
        ["black", "red", "sandy"],
        index=0,
        format_func=lambda x: x if lang == "en" else SOIL_KN[x],
        key=f"soil_input_{v}",
    )

    # ── Season ──
    st.markdown(f"""
    <div style="padding: 0;">
        <div style="display: flex; align-items: center; gap: 0.5rem; margin: 1rem 0 0.5rem 0;">
            <div style="width: 3px; height: 1rem; background: #2A5C2A; border-radius: 2px; flex-shrink: 0;"></div>
            <p style="font-size: 0.78rem; font-weight: 700; color: #245B32; text-transform: uppercase; letter-spacing: 1.2px; margin: 0; font-family: 'Inter', 'Noto Sans Kannada', sans-serif;">
                {t_fn("form_season_crop")}
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    season_key = f"season_input_{v}"
    season_index = None if season_key in st.session_state else 0
    season = st.radio(
        t_fn("season"),
        ["kharif", "rabi"],
        horizontal=True,
        format_func=lambda x: SEASON[x][i],
        index=season_index,
        key=season_key,
    )

    # ── Crop History ──
    st.markdown(f"""
    <div style="padding: 0;">
        <div style="display: flex; align-items: center; gap: 0.5rem; margin: 1rem 0 0.5rem 0;">
            <div style="width: 3px; height: 1rem; background: #2A5C2A; border-radius: 2px; flex-shrink: 0;"></div>
            <p style="font-size: 0.78rem; font-weight: 700; color: #245B32; text-transform: uppercase; letter-spacing: 1.2px; margin: 0; font-family: 'Inter', 'Noto Sans Kannada', sans-serif;">
                {t_fn("form_crop_history")}
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    all_last = list(sc.crop_info) + list(sc.other_info)
    last_crop = st.selectbox(
        t_fn("last"),
        all_last,
        format_func=lambda c: sc.crop_word(lang, c),
        key=f"last_crop_input_{v}",
    )
    prev_label = "Crop before that" if lang == "en" else t_fn("prev")
    prev_crop = st.selectbox(
        prev_label,
        [None] + list(sc.crop_info),
        index=0,
        format_func=lambda c: "-" if c is None else sc.crop_word(lang, c),
        key=f"prev_crop_input_{v}",
    )

    # ── Preferences ──
    st.markdown(f"""
    <div style="padding: 0;">
        <div style="display: flex; align-items: center; gap: 0.5rem; margin: 1rem 0 0.5rem 0;">
            <div style="width: 3px; height: 1rem; background: #2A5C2A; border-radius: 2px; flex-shrink: 0;"></div>
            <p style="font-size: 0.78rem; font-weight: 700; color: #245B32; text-transform: uppercase; letter-spacing: 1.2px; margin: 0; font-family: 'Inter', 'Noto Sans Kannada', sans-serif;">
                {t_fn("form_preferences")}
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    irrigation_key = f"irrigation_input_{v}"
    irr_index = None if irrigation_key in st.session_state else 1

    irrigation = st.radio(
        t_fn("irr"),
        [True, False],
        horizontal=True,
        format_func=lambda x: t_fn("yes") if x else t_fn("no"),
        index=irr_index,
        key=irrigation_key,
    )
    st.session_state["irrigation"] = irrigation

    priority_key = f"priority_input_{v}"
    priority_index = None if priority_key in st.session_state else 0
    priority = st.radio(
        t_fn("pri"),
        list(PRIORITY),
        format_func=lambda x: PRIORITY[x][i],
        index=priority_index,
        key=priority_key,
    )

    # Usual crop for comparison
    season_crops = [c for c, val in sc.crop_info.items() if val["season"] == season]
    usual_key = f"usual_crop_input_{v}"
    usual_options = ["Select"] + season_crops
    if usual_key in st.session_state and st.session_state[usual_key] not in usual_options:
        st.session_state[usual_key] = "Select"

    usual = st.selectbox(
        t_fn("usual_crop"),
        usual_options,
        index=0,
        format_func=lambda c: "Select" if c == "Select" else sc.crop_word(lang, c),
        key=usual_key,
    )

    # Bottom cap of form card
    st.markdown("""
    <div style="
        background: #F8F6F1;
        border-radius: 0 0 16px 16px;
        padding: 0.8rem 1.4rem 1rem 1.4rem;
        border: 1.5px solid #DDE8D7;
        border-top: none;
        box-shadow: 0 4px 12px rgba(0,0,0,0.06);
        margin-bottom: 1rem;
    ">
    </div>
    """, unsafe_allow_html=True)

    submitted = st.button(t_fn("go"), type="primary", use_container_width=True, key=f"go_btn_{v}")

    return {
        "taluk": taluk,
        "soil": soil,
        "season": season,
        "last_crop": last_crop,
        "prev_crop": prev_crop,
        "irrigation": irrigation,
        "priority": priority,
        "usual": usual,
    }, submitted


# =====================================================================
# SECTION: Recommendation Results
# =====================================================================
@st.cache_data(show_spinner=False)
def _compute_results(zone, soil, season, last_crop, prev_crop, irrigation, priority, usual_choice, lang):
    kw = dict(
        zone=zone,
        soil=soil,
        season=season,
        last_crop=last_crop,
        prev_crop=prev_crop,
        irrigation=irrigation,
        priority=priority,
    )
    r = sc.recommend_with_ties(lang=lang, **kw)
    cs = sc.compare_strategies(usual_choice, lang=lang, **kw)
    ac = sc.assumption_check(**kw)
    return r, cs, ac


def render_results(inputs, lang, i, t_fn):
    """Render recommendation results."""
    season_crops = [c for c, val in sc.crop_info.items() if val["season"] == inputs["season"]]
    usual_choice = inputs["usual"] if inputs.get("usual") in season_crops else None
    try:
        zone = sc.zone_for(inputs["taluk"])
        r, cs, ac = _compute_results(
            zone=zone,
            soil=inputs["soil"],
            season=inputs["season"],
            last_crop=inputs["last_crop"],
            prev_crop=inputs["prev_crop"],
            irrigation=inputs["irrigation"],
            priority=inputs["priority"],
            usual_choice=usual_choice,
            lang=lang,
        )
    except ValueError:
        st.warning(f"⚠ {t_fn('warning')}")
        return

    # Results header
    st.markdown(clean_html(f"""
    <div class="dark-header-card" style="
        background: linear-gradient(145deg, #1B3D1B 0%, #2A5C2A 50%, #3A6E3A 100%);
        border-radius: 16px;
        padding: 1.4rem 1.4rem;
        margin: 1.4rem 0 1.1rem 0;
        text-align: center;
        box-shadow: 0 6px 20px rgba(27,61,27,0.25), 0 2px 6px rgba(0,0,0,0.08);
        position: relative;
        overflow: hidden;
    ">
        <div style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: radial-gradient(ellipse at 70% 30%, rgba(155,189,141,0.12) 0%, transparent 60%); pointer-events: none;"></div>
        <div style="font-size: 0.72rem; letter-spacing: 2px; color: #FFFFFF !important; text-transform: uppercase; margin-bottom: 0.4rem; font-family: 'Inter', sans-serif; font-weight: 700; opacity: 0.95;">✓ {"Analysis complete" if lang == "en" else "ವಿಶ್ಲೇಷಣೆ ಪೂರ್ಣ"}</div>
        <h2 style="color: #FFFFFF !important; font-size: 1.25rem; font-weight: 800; margin: 0; font-family: 'Inter', 'Noto Sans Kannada', sans-serif; letter-spacing: -0.01em;">
            {t_fn("results_title")}
        </h2>
    </div>
    """), unsafe_allow_html=True)

    # Warnings
    for w in r["warnings"]:
        st.markdown(clean_html(f"""
        <div style="
            background: #FFFBEE;
            border-left: 4px solid #C49A00;
            border-radius: 10px;
            padding: 0.9rem 1.1rem;
            margin-bottom: 0.65rem;
            font-size: 0.88rem;
            color: #6B4F00;
            font-family: 'Inter', 'Noto Sans Kannada', sans-serif;
            line-height: 1.55;
            box-shadow: 0 1px 4px rgba(196,154,0,0.10);
        ">
            <strong style="color: #8A6300;">⚠ {t_fn("warning")}:</strong> {w}
        </div>
        """), unsafe_allow_html=True)

    # Crop cards
    for idx, x in enumerate(r["ranked"]):
        card_html = render_crop_card(x, lang, t_fn, is_top=(idx == 0))
        st.markdown(card_html, unsafe_allow_html=True)

    # NASA facts
    zone_key = zone.capitalize() if zone.capitalize() in ZONE_FACTS else zone
    zone_label = sc.WORDS[lang]["zones"].get(zone_key, zone_key)
    dry_spell_pct = ZONE_FACTS[zone_key] if isinstance(ZONE_FACTS.get(zone_key), (int, float, str)) else ZONE_FACTS[zone_key][1 if lang == "kn" else 0]
    if lang == "kn":
        nasa_fact_text = f"🛰️ <strong>ನಾಸಾ POWER 1981–2025</strong> (ಮಾದರಿ ಅಂದಾಜು, {zone_label} ವಲಯ): ಜುಲೈ–ಆಗಸ್ಟ್‌ನಲ್ಲಿ 7+ ದಿನಗಳ ಒಣ ಅವಧಿ <strong>{dry_spell_pct}%</strong> ವರ್ಷಗಳಲ್ಲಿ ಸಂಭವಿಸಿದೆ."
    else:
        nasa_fact_text = f"🛰️ <strong>NASA POWER 1981–2025</strong> (model estimate, {zone_key} zone): a dry spell of 7+ days in July–August happened in <strong>{dry_spell_pct}%</strong> of years."

    st.markdown(clean_html(f"""
    <div style="
        background: #E8F2FC;
        border-left: 4px solid #3A87CC;
        border-radius: 10px;
        padding: 0.9rem 1.1rem;
        margin: 0.9rem 0;
        font-size: 0.87rem;
        color: #1A3A5C;
        line-height: 1.55;
        font-family: 'Inter', 'Noto Sans Kannada', sans-serif;
        box-shadow: 0 1px 4px rgba(58,135,204,0.08);
    ">
        {nasa_fact_text}
    </div>
    """), unsafe_allow_html=True)

    # ── Compare 3 strategies ──
    strat_note = t_fn("strategies_note")
    note_html = f' <span style="font-size: 0.78rem; color: #526E59; font-weight: 500; margin-left: 0.3rem;">{strat_note}</span>' if strat_note else ""
    st.markdown(clean_html(f"""
    <div style="
        background: #FFFFFF;
        border-radius: 16px 16px 0 0;
        padding: 1.1rem 1.3rem 0.6rem 1.3rem;
        margin-top: 1.4rem;
        border-bottom: 2px solid #DDE8D7;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
    ">
        <h3 style="color: #2A5C2A !important; font-size: 1.0rem; font-weight: 700; margin: 0; font-family: 'Inter', 'Noto Sans Kannada', sans-serif; letter-spacing: -0.01em; display: flex; align-items: center; gap: 0.5rem;">
            <span style="display: inline-block; width: 4px; height: 1.0rem; background: #2A5C2A; border-radius: 2px; flex-shrink: 0;"></span>
            {t_fn("strategies_title")}{note_html}
        </h3>
    </div>
    """), unsafe_allow_html=True)

    if cs:
        strategy_icons = {
            "usual": "🌾",
            "alt_1": "🌱",
            "alt_2": "🌿",
            "alt_3": "🌿",
            "Your usual choice": "🌾",
            "Alternative 1": "🌱",
            "Alternative 2": "🌿",
            "Alternative 3": "🌿",
        }
        for s in cs["strategies"]:
            tag = f" — {t_fn('equal')}" if s["tied_with_another"] else ""
            st_icon = strategy_icons.get(s.get("key"), strategy_icons.get(s.get("label"), "🌱"))
            crop_disp = s["name_kn"] if lang == "kn" else sc.crop_word(lang, s["crop"])
            with st.expander(
                f"{s.get('label_text', s['label'])}: {crop_disp} ({s['total']}/{s['max_total']}){tag}",
                icon=st_icon,
            ):
                # Why suggested
                st.markdown(f"**{t_fn('why_suggested')}**")
                for a in s["why"]:
                    st.markdown(f"- {a}")

                # Evidence
                st.markdown(
                    f"**{t_fn('evidence')}**: {s['evidence']} ({s['evidence_strength']})"
                )

                # Benefits
                st.markdown(f"**{t_fn('benefits')}**")
                for a in s["benefits"]:
                    st.markdown(f"- {a}")

                # Information gaps
                st.markdown(f"**{t_fn('info_gaps')}**")
                for a in s["gaps"]:
                    st.markdown(f"- {a}")

                # Risks
                st.markdown(f"**{t_fn('risks')}**")
                for a in s["risks"]:
                    st.markdown(f"- {a}")

    # ── Assumption / stability check ──
    st.markdown(f"""
    <div style="margin-top: 1.2rem; margin-bottom: 0.4rem;">
        <div style="display: flex; align-items: center; gap: 0.5rem;">
            <div style="width: 3px; height: 1rem; background: #2A5C2A; border-radius: 2px; flex-shrink: 0;"></div>
            <p style="font-size: 0.78rem; font-weight: 700; color: #245B32; text-transform: uppercase; letter-spacing: 1.2px; margin: 0; font-family: 'Inter', 'Noto Sans Kannada', sans-serif;">
                {t_fn("assumption_title")}
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if ac:
        if lang == "kn":
            ac_msg = (
                "ದೃಢಪಡಿಸದ ನೀರಿನ ಅವಶ್ಯಕತೆಗಳು ತಪ್ಪಾಗಿದ್ದರೂ ಅತ್ಯುತ್ತಮ ಆಯ್ಕೆಯು ಬದಲಾಗುವುದಿಲ್ಲ."
                if ac["status"] == "stable"
                else "ಅತ್ಯುತ್ತಮ ಆಯ್ಕೆಯು ಯಾವುದೇ ತಜ್ಞರು ದೃಢಪಡಿಸದ ನೀರಿನ ಅವಶ್ಯಕತೆಯ ಮೇಲೆ ಅವಲಂಬಿತವಾಗಿದೆ. ದಯವಿಟ್ಟು ಸ್ಥಳೀಯ ತಜ್ಞರನ್ನು ಕೇಳಿ."
            )
        else:
            ac_msg = ac["message"]

        if ac["status"] == "stable":
            st.markdown(clean_html(f"""
            <div style="
                background: #EBF5EC;
                border-left: 4px solid #3D9A42;
                border-radius: 10px;
                padding: 0.9rem 1.1rem;
                margin-bottom: 0.6rem;
                font-size: 0.88rem;
                color: #1F5E22;
                line-height: 1.55;
                font-family: 'Inter', 'Noto Sans Kannada', sans-serif;
                box-shadow: 0 1px 4px rgba(61,154,66,0.08);
            ">
                ✓ {ac_msg}
            </div>
            """), unsafe_allow_html=True)
        else:
            st.markdown(clean_html(f"""
            <div style="
                background: #FFFBEE;
                border-left: 4px solid #C49A00;
                border-radius: 10px;
                padding: 0.9rem 1.1rem;
                margin-bottom: 0.6rem;
                font-size: 0.88rem;
                color: #6B4F00;
                line-height: 1.55;
                font-family: 'Inter', 'Noto Sans Kannada', sans-serif;
                box-shadow: 0 1px 4px rgba(196,154,0,0.10);
            ">
                ⚠ {ac_msg}
            </div>
            """), unsafe_allow_html=True)


# =====================================================================
# MAIN APPLICATION
# =====================================================================
def main():
    # Language selector
    lang, i, t = setup_language()
    v = st.session_state.get("lang_version", 0)

    # Navigation state
    if "page" not in st.session_state:
        q_page = st.query_params.get("page")
        st.session_state["page"] = q_page if q_page in ("home", "form") else "home"
    if st.query_params.get("go") == "1" and "go" not in st.session_state:
        st.session_state["go"] = True

    page = st.session_state["page"]

    # ── HOME / LANDING ──
    if page == "home":
        render_hero(t, lang)
        if st.button(t("start_btn"), type="primary", use_container_width=True, key=f"start_btn_{v}"):
            st.session_state["page"] = "form"
            st.rerun()

    # ── FORM ──
    elif page == "form":
        # Back to home
        if st.button("← " + ("Home" if lang == "en" else "ಮುಖಪುಟ"), type="primary", key=f"back_home_{v}"):
            st.session_state["page"] = "home"
            st.session_state.pop("go", None)
            st.session_state.pop("inputs", None)
            st.rerun()

        inputs, submitted = render_form(lang, i, t)

        if submitted or (st.session_state.get("go") and "inputs" not in st.session_state):
            st.session_state["go"] = True
            st.session_state["inputs"] = inputs

        # ── RESULTS ──
        if st.session_state.get("go") and "inputs" in st.session_state:
            render_results(st.session_state["inputs"], lang, i, t)

            # New recommendation button
            st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
            if st.button(t("back_to_top"), type="primary", use_container_width=True, key=f"new_rec_{v}"):
                st.session_state.pop("go", None)
                st.session_state.pop("inputs", None)
                st.session_state.pop("irrigation", None)
                st.rerun()

    # ── Footer / Disclaimer ──
    st.markdown("""
    <div style="margin-top: 2rem; padding-top: 1rem; border-top: 1.5px solid #DDE8D7;"></div>
    """, unsafe_allow_html=True)

    st.markdown(clean_html(f"""
    <div style="
        background: #F4F8F2;
        border-left: 4px solid #2A5C2A;
        border-radius: 10px;
        padding: 1.1rem 1.3rem;
        font-size: 0.95rem;
        font-weight: 600;
        color: #122012;
        line-height: 1.65;
        font-family: 'Inter', 'Noto Sans Kannada', sans-serif;
        box-shadow: 0 1px 4px rgba(0,0,0,0.05);
        margin-bottom: 0.6rem;
    ">
        {t("disclaimer")}
    </div>
    """), unsafe_allow_html=True)

    # Branding footer
    st.markdown("""
    <div style="
        text-align: center;
        padding: 1rem 0 0.6rem 0;
        color: #526E59;
        font-size: 0.75rem;
        font-family: 'Inter', sans-serif;
        letter-spacing: 0.03em;
    ">
        Field Shift — NASA Space Apps Challenge
    </div>
    """, unsafe_allow_html=True)


main()
