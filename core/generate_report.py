"""
Build an HTML mapping report: each user field -> FAIR eDNA candidate(s) with scores.
"""

import html
import os
from pathlib import Path
from core.normalization import normalize
from data_loading.data_loading import get_term_value, get_term_description


def _example_str(terms_dict, term):
    value = get_term_value(terms_dict.get(term, ''))
    return '' if value is None else str(value)


def _desc_str(terms_dict, term):
    return get_term_description(terms_dict.get(term, '')) or ''


def _resolve_original(norm_term, terms_dict):
    return next((t for t in terms_dict if normalize(t) == norm_term), norm_term)


def _build_rows(
    exact_matches,
    normalized_matches,
    fuzzy_matches,
    semantic_matches_scibert,
    user_terms_w_data,
    faire_terms_w_data,
    bert_threshold,
    num_matches,
):
    """
    One row per user field.
    Each row: user term info + method + ordered list of FAIR eDNA candidates (term, score_pct, value, description).
    """
    claimed = set()
    rows = []

    # Exact name matches
    for user_term, faire_term in exact_matches.items():
        claimed.add(user_term)
        rows.append({
            'user_term': user_term,
            'user_value': _example_str(user_terms_w_data, user_term),
            'user_description': _desc_str(user_terms_w_data, user_term),
            'method': 'exact',
            'candidates': [{
                'faire_term': faire_term,
                'score_pct': 100.0,
                'faire_value': _example_str(faire_terms_w_data, faire_term),
                'faire_description': _desc_str(faire_terms_w_data, faire_term),
            }],
        })

    # Normalized name matches (keys are normalized strings)
    for norm_user, norm_faire in normalized_matches.items():
        user_term = _resolve_original(norm_user, user_terms_w_data)
        if user_term in claimed:
            continue
        faire_term = _resolve_original(norm_faire, faire_terms_w_data)
        claimed.add(user_term)
        rows.append({
            'user_term': user_term,
            'user_value': _example_str(user_terms_w_data, user_term),
            'user_description': _desc_str(user_terms_w_data, user_term),
            'method': 'normalized',
            'candidates': [{
                'faire_term': faire_term,
                'score_pct': 100.0,
                'faire_value': _example_str(faire_terms_w_data, faire_term),
                'faire_description': _desc_str(faire_terms_w_data, faire_term),
            }],
        })

    # Fuzzy: dict is {norm_template: (norm_user, score 0-100)}
    fuzzy_by_user = {}
    for norm_faire, (norm_user, score) in (fuzzy_matches or {}).items():
        if norm_user not in fuzzy_by_user or score > fuzzy_by_user[norm_user][1]:
            fuzzy_by_user[norm_user] = (norm_faire, score)

    for norm_user, (norm_faire, score) in fuzzy_by_user.items():
        user_term = _resolve_original(norm_user, user_terms_w_data)
        if user_term in claimed:
            continue
        faire_term = _resolve_original(norm_faire, faire_terms_w_data)
        claimed.add(user_term)
        rows.append({
            'user_term': user_term,
            'user_value': _example_str(user_terms_w_data, user_term),
            'user_description': _desc_str(user_terms_w_data, user_term),
            'method': 'fuzzy',
            'candidates': [{
                'faire_term': faire_term,
                'score_pct': float(score),
                'faire_value': _example_str(faire_terms_w_data, faire_term),
                'faire_description': _desc_str(faire_terms_w_data, faire_term),
            }],
        })

    # Semantic: list of (faire_term, score 0-1, user_data, faire_data)
    for user_term, matches in (semantic_matches_scibert or {}).items():
        if user_term in claimed:
            continue
        candidates = []
        for match, score, _, _ in matches[:num_matches]:
            if score < bert_threshold:
                continue
            candidates.append({
                'faire_term': match,
                'score_pct': float(score) * 100.0,
                'faire_value': _example_str(faire_terms_w_data, match),
                'faire_description': _desc_str(faire_terms_w_data, match),
            })
        claimed.add(user_term)
        rows.append({
            'user_term': user_term,
            'user_value': _example_str(user_terms_w_data, user_term),
            'user_description': _desc_str(user_terms_w_data, user_term),
            'method': 'semantic' if candidates else 'unmatched',
            'candidates': candidates,
        })

    # Any user fields never touched (e.g. filtered out earlier)
    for user_term in user_terms_w_data:
        if user_term in claimed:
            continue
        rows.append({
            'user_term': user_term,
            'user_value': _example_str(user_terms_w_data, user_term),
            'user_description': _desc_str(user_terms_w_data, user_term),
            'method': 'unmatched',
            'candidates': [],
        })

    # Stable order: follow user JSON key order
    order = {term: i for i, term in enumerate(user_terms_w_data.keys())}
    rows.sort(key=lambda r: order.get(r['user_term'], 10**9))
    return rows


def _method_label(method):
    return {
        'exact': 'Exact name',
        'normalized': 'Normalized name',
        'fuzzy': 'Fuzzy name',
        'semantic': 'Semantic (AI)',
        'unmatched': 'No match',
    }.get(method, method)


def generate_report(
    normalized_matches,
    exact_matches,
    semantic_matches_scibert,
    new_terms,
    output_file,
    user_terms_w_data,
    noaa_terms_w_data,
    bert_threshold=0.3,
    num_matches=5,
    fuzzy_matches=None,
):
    rows = _build_rows(
        exact_matches,
        normalized_matches,
        fuzzy_matches or {},
        semantic_matches_scibert,
        user_terms_w_data,
        noaa_terms_w_data,
        bert_threshold,
        num_matches,
    )

    n_exact = sum(1 for r in rows if r['method'] == 'exact')
    n_norm = sum(1 for r in rows if r['method'] == 'normalized')
    n_fuzzy = sum(1 for r in rows if r['method'] == 'fuzzy')
    n_sem = sum(1 for r in rows if r['method'] == 'semantic')
    n_none = sum(1 for r in rows if r['method'] == 'unmatched')

    # If caller still passes a .csv path, write .html beside it
    if output_file.lower().endswith('.csv'):
        output_file = output_file[:-4] + '.html'

    repo_root = Path(__file__).resolve().parent.parent
    out_dir = Path(output_file).resolve().parent
    logo_href = Path(os.path.relpath(repo_root / 'script_dependencies' / 'faire_logo.png', out_dir)).as_posix()
    icon_href = Path(os.path.relpath(repo_root / 'script_dependencies' / 'faire_icon.svg', out_dir)).as_posix()

    field_rows_html = []

    for r in rows:
        esc_user = html.escape(r['user_term'])
        method = r['method']
        best = r['candidates'][0] if r['candidates'] else None
        best_term = html.escape(best['faire_term']) if best else '-'
        best_score = f"{best['score_pct']:.0f}%" if best else '-'
        n_alts = max(0, len(r['candidates']) - 1)

        user_val = html.escape(r['user_value']) if r['user_value'] != '' else '-'
        user_desc = html.escape(r['user_description']) if r['user_description'] else 'No description'
        user_tip = html.escape(
            (r['user_description'] or 'No description')
            + ((' | Example: ' + str(r['user_value'])) if r['user_value'] not in (None, '') else '')
        )

        best_desc = html.escape(best['faire_description']) if best and best['faire_description'] else 'No description'
        best_val = html.escape(best['faire_value']) if best and best['faire_value'] != '' else '-'
        best_tip = ''
        if best:
            best_tip = html.escape(
                (best['faire_description'] or 'No description')
                + ((' | Example: ' + str(best['faire_value'])) if best['faire_value'] not in (None, '') else '')
            )

        alt_rows = []
        for i, c in enumerate(r['candidates'][1:], start=2):
            c_desc = html.escape(c['faire_description']) if c['faire_description'] else 'No description'
            c_val = html.escape(c['faire_value']) if c['faire_value'] != '' else '-'
            c_tip = html.escape(
                (c['faire_description'] or 'No description')
                + ((' | Example: ' + str(c['faire_value'])) if c['faire_value'] not in (None, '') else '')
            )
            alt_rows.append(f"""
            <tr>
              <td>{i}</td>
              <td>
                <button type="button" class="term-btn" title="{c_tip}"
                  data-title="{html.escape(c['faire_term'])}"
                  data-desc="{c_desc}"
                  data-example="{c_val}">
                  {html.escape(c['faire_term'])}
                </button>
              </td>
              <td class="score">{c['score_pct']:.0f}%</td>
            </tr>""")

        if alt_rows:
            alts_block = f"""
            <div class="alts">
              <div class="alts-label">Other candidates</div>
              <table>
                <thead><tr><th>#</th><th>FAIR eDNA term</th><th>Score</th></tr></thead>
                <tbody>{''.join(alt_rows)}</tbody>
              </table>
            </div>"""
        elif best:
            alts_block = '<p class="muted">No alternate candidates for this field.</p>'
        else:
            alts_block = '<p class="muted">No match above the score threshold.</p>'

        expand_hint = f'{n_alts} more' if n_alts else 'info'
        disabled_attr = ' disabled' if not best else ''

        field_rows_html.append(f"""
        <details class="map-row">
          <summary>
            <span class="col-user">
              <button type="button" class="term-btn" title="{user_tip}"
                data-title="{esc_user}"
                data-desc="{user_desc}"
                data-example="{user_val}">
                {esc_user}
              </button>
            </span>
            <span class="col-match">
              <button type="button" class="term-btn" title="{best_tip}"
                data-title="{best_term}"
                data-desc="{best_desc}"
                data-example="{best_val}"{disabled_attr}>
                {best_term}
              </button>
            </span>
            <span class="col-method">{html.escape(_method_label(method))}</span>
            <span class="col-score score">{best_score}</span>
            <span class="col-more">{expand_hint}</span>
          </summary>
          <div class="expand">
            <div class="pair">
              <div>
                <div class="label">Your field</div>
                <div><strong>{esc_user}</strong></div>
                <p>{user_desc}</p>
                <p class="muted"><strong>Example:</strong> {user_val}</p>
              </div>
              <div>
                <div class="label">Best FAIR eDNA match</div>
                <div><strong>{best_term}</strong></div>
                <p>{best_desc if best else '-'}</p>
                <p class="muted"><strong>Example:</strong> {best_val if best else '-'}</p>
              </div>
            </div>
            {alts_block}
          </div>
        </details>""")

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>TermMatchAI | User to FAIR eDNA</title>
  <style>
    :root {{
      --green: #92D050;
      --green-dark: #6fad35;
      --ink: #333333;
      --muted: #666666;
      --line: #e6e6e6;
      --header: #f2f2f2;
      --bg: #ffffff;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      color: var(--ink);
      background: var(--bg);
      font-family: Arial, Helvetica, sans-serif;
      font-size: 15px;
      line-height: 1.45;
    }}
    .topbar {{
      background: var(--header);
      border-bottom: 3px solid var(--green);
      padding: 0.75rem 1.5rem;
      display: flex;
      align-items: center;
      gap: 0.85rem;
    }}
    .topbar img.icon {{
      height: 64px;
      width: auto;
      display: block;
    }}
    .topbar .titles {{ display: flex; flex-direction: column; gap: 0.1rem; }}
    .topbar .titles strong {{ font-size: 1.05rem; }}
    .topbar .titles span {{ color: var(--muted); font-size: 0.88rem; }}
    .wrap {{ max-width: 980px; margin: 0 auto; padding: 1.25rem 1.5rem 2.5rem; }}
    .brand-logo {{ margin: 0 0 1.5rem; }}
    .brand-logo img {{ height: 160px; width: auto; display: block; }}
    h1 {{
      margin: 0 0 0.3rem;
      font-size: 1.35rem;
      font-weight: 700;
    }}
    .sub {{ margin: 0 0 0.85rem; color: var(--muted); }}
    .counts {{
      margin: 0 0 1.25rem;
      color: var(--muted);
      font-size: 0.9rem;
    }}
    .counts b {{ color: var(--ink); }}
    .table-head {{
      display: grid;
      grid-template-columns: minmax(0, 1.3fr) minmax(0, 1.3fr) 7.5rem 4rem 4.5rem;
      gap: 0.5rem;
      padding: 0.45rem 0.35rem;
      border-bottom: 2px solid var(--green);
      font-size: 0.75rem;
      text-transform: uppercase;
      letter-spacing: 0.03em;
      color: var(--muted);
      font-weight: 700;
    }}
    details.map-row {{ border-bottom: 1px solid var(--line); }}
    details.map-row > summary {{
      list-style: none;
      cursor: pointer;
      display: grid;
      grid-template-columns: minmax(0, 1.3fr) minmax(0, 1.3fr) 7.5rem 4rem 4.5rem;
      gap: 0.5rem;
      align-items: center;
      padding: 0.65rem 0.35rem;
    }}
    details.map-row > summary::-webkit-details-marker {{ display: none; }}
    details.map-row[open] > summary {{ background: #fafafa; }}
    .col-score, .score {{
      font-variant-numeric: tabular-nums;
      font-weight: 700;
      color: var(--green-dark);
    }}
    .col-more {{
      color: var(--muted);
      font-size: 0.82rem;
      text-align: right;
    }}
    .col-method {{ color: var(--muted); font-size: 0.9rem; }}
    button.term-btn {{
      background: none;
      border: none;
      padding: 0;
      margin: 0;
      font: inherit;
      color: var(--green-dark);
      cursor: pointer;
      text-align: left;
    }}
    button.term-btn:hover {{ text-decoration: underline; }}
    button.term-btn:disabled {{
      color: var(--ink);
      cursor: default;
      text-decoration: none;
    }}
    .expand {{
      padding: 0.25rem 0.35rem 1rem;
      background: #fcfcfc;
    }}
    .pair {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 1rem;
      margin-bottom: 0.85rem;
    }}
    .pair .label {{
      font-size: 0.75rem;
      text-transform: uppercase;
      letter-spacing: 0.03em;
      color: var(--muted);
      font-weight: 700;
      margin-bottom: 0.2rem;
    }}
    .pair p {{ margin: 0.35rem 0; }}
    .alts-label {{
      font-size: 0.75rem;
      text-transform: uppercase;
      letter-spacing: 0.03em;
      color: var(--muted);
      font-weight: 700;
      margin: 0.5rem 0 0.35rem;
    }}
    .alts table {{ width: 100%; border-collapse: collapse; }}
    .alts th, .alts td {{
      text-align: left;
      padding: 0.4rem 0.3rem;
      border-bottom: 1px solid var(--line);
      vertical-align: top;
    }}
    .alts th {{
      font-size: 0.72rem;
      text-transform: uppercase;
      letter-spacing: 0.03em;
      color: var(--muted);
    }}
    .muted {{ color: var(--muted); font-size: 0.9rem; }}
    footer {{
      margin-top: 1.75rem;
      padding-top: 0.85rem;
      border-top: 1px solid var(--line);
      color: var(--muted);
      font-size: 0.85rem;
    }}
    .popover {{
      position: fixed;
      z-index: 20;
      max-width: 340px;
      background: #fff;
      border: 1px solid var(--line);
      border-top: 3px solid var(--green);
      box-shadow: 0 8px 24px rgba(0,0,0,0.12);
      padding: 0.75rem 0.85rem;
      display: none;
    }}
    .popover.open {{ display: block; }}
    .popover h3 {{ margin: 0 0 0.4rem; font-size: 0.95rem; }}
    .popover p {{ margin: 0.3rem 0; font-size: 0.88rem; }}
    .popover .close {{
      float: right;
      border: none;
      background: none;
      font-size: 1.1rem;
      cursor: pointer;
      color: var(--muted);
      line-height: 1;
    }}
    @media (max-width: 720px) {{
      .table-head, details.map-row > summary {{
        grid-template-columns: minmax(0, 1fr) minmax(0, 1fr) 3.5rem;
      }}
      .col-method, .table-head span:nth-child(3),
      .col-more, .table-head span:nth-child(5) {{ display: none; }}
      .pair {{ grid-template-columns: 1fr; }}
      .brand-logo img {{ height: 120px; }}
    }}
  </style>
</head>
<body>
  <div class="topbar">
    <img class="icon" src="{html.escape(icon_href)}" alt="" />
    <div class="titles">
      <strong>TermMatchAI</strong>
      <span>User standard mapped to FAIR eDNA</span>
    </div>
  </div>

  <div class="wrap">
    <div class="brand-logo">
      <img src="{html.escape(logo_href)}" alt="Make eDNA FAIR" />
    </div>

    <h1>TermMatchAI Report</h1>
    <p class="sub">
      Click each row to see alternate matches.
      You can hover on term names or click for more information.
    </p>
    <p class="counts">
      <b>{len(rows)}</b> fields ·
      <b>{n_exact}</b> exact ·
      <b>{n_norm}</b> normalized ·
      <b>{n_fuzzy}</b> fuzzy ·
      <b>{n_sem}</b> semantic ·
      <b>{n_none}</b> unmatched
    </p>

    <div class="table-head">
      <span>Your field</span>
      <span>FAIR eDNA match</span>
      <span>Method</span>
      <span>Score</span>
      <span></span>
    </div>
    {''.join(field_rows_html)}

    <footer>
      Exact/normalized = 100%. Fuzzy = name similarity. Semantic = description meaning + field-name tokens
      (threshold {bert_threshold:.0%}).
    </footer>
  </div>

  <div id="popover" class="popover" role="dialog" aria-live="polite">
    <button type="button" class="close" aria-label="Close">&times;</button>
    <h3 id="pop-title"></h3>
    <p id="pop-desc"></p>
    <p class="muted"><strong>Example:</strong> <span id="pop-example"></span></p>
  </div>

  <script>
    (function () {{
      var pop = document.getElementById('popover');
      var title = document.getElementById('pop-title');
      var desc = document.getElementById('pop-desc');
      var example = document.getElementById('pop-example');

      function hide() {{ pop.classList.remove('open'); }}

      pop.querySelector('.close').addEventListener('click', function (e) {{
        e.stopPropagation();
        hide();
      }});

      document.addEventListener('click', function (e) {{
        var btn = e.target.closest('button.term-btn');
        if (!btn || btn.disabled) {{
          if (!e.target.closest('#popover')) hide();
          return;
        }}
        e.preventDefault();
        e.stopPropagation();
        title.textContent = btn.getAttribute('data-title') || '';
        desc.textContent = btn.getAttribute('data-desc') || '';
        example.textContent = btn.getAttribute('data-example') || '-';
        pop.classList.add('open');
        var rect = btn.getBoundingClientRect();
        var left = Math.min(rect.left, window.innerWidth - 360);
        var top = rect.bottom + 8;
        if (top + 160 > window.innerHeight) top = Math.max(8, rect.top - 160);
        pop.style.left = Math.max(8, left) + 'px';
        pop.style.top = top + 'px';
      }});
    }})();
  </script>
</body>
</html>
"""

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(page)

    return output_file
