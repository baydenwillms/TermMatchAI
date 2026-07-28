"""
Build an HTML mapping report: each user field -> FAIRe candidate(s) with scores.
"""

import html
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
    Each row: user term info + method + ordered list of FAIRe candidates (term, score_pct, value, description).
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

    summary_rows_html = []
    detail_blocks_html = []

    for r in rows:
        esc_user = html.escape(r['user_term'])
        method = r['method']
        best = r['candidates'][0] if r['candidates'] else None
        best_term = html.escape(best['faire_term']) if best else '-'
        best_score = f"{best['score_pct']:.1f}%" if best else '-'
        bar_w = f"{min(best['score_pct'], 100):.1f}" if best else '0'

        summary_rows_html.append(f"""
        <tr class="method-{html.escape(method)}">
          <td><a href="#field-{esc_user}">{esc_user}</a></td>
          <td>{best_term}</td>
          <td><span class="badge badge-{html.escape(method)}">{html.escape(_method_label(method))}</span></td>
          <td class="score-cell">
            <div class="score-bar-wrap"><div class="score-bar" style="width:{bar_w}%"></div></div>
            <span class="score-num">{best_score}</span>
          </td>
        </tr>""")

        # Per-field detail
        user_val = html.escape(r['user_value']) if r['user_value'] != '' else '<em>none</em>'
        user_desc = html.escape(r['user_description']) if r['user_description'] else '<em>No description provided</em>'

        cand_rows = []
        if not r['candidates']:
            cand_rows.append('<tr><td colspan="4"><em>No FAIRe match found above the score threshold.</em></td></tr>')
        else:
            for i, c in enumerate(r['candidates']):
                rank = 'Best' if i == 0 else f'#{i + 1}'
                cand_rows.append(f"""
                <tr>
                  <td>{rank}</td>
                  <td><code>{html.escape(c['faire_term'])}</code></td>
                  <td class="score-cell">
                    <div class="score-bar-wrap"><div class="score-bar" style="width:{min(c['score_pct'], 100):.1f}%"></div></div>
                    <span class="score-num">{c['score_pct']:.1f}%</span>
                  </td>
                  <td>
                    <div class="meta"><strong>Example:</strong> {html.escape(c['faire_value']) if c['faire_value'] != '' else '<em>none</em>'}</div>
                    <div class="meta muted">{html.escape(c['faire_description']) if c['faire_description'] else ''}</div>
                  </td>
                </tr>""")

        detail_blocks_html.append(f"""
        <section class="field-card" id="field-{esc_user}">
          <header>
            <h3><code>{esc_user}</code></h3>
            <span class="badge badge-{html.escape(method)}">{html.escape(_method_label(method))}</span>
          </header>
          <div class="field-body">
            <p class="desc">{user_desc}</p>
            <p class="example"><strong>Your example value:</strong> {user_val}</p>
            <table class="candidates">
              <thead>
                <tr>
                  <th>Rank</th>
                  <th>FAIRe term</th>
                  <th>Score</th>
                  <th>FAIRe example / description</th>
                </tr>
              </thead>
              <tbody>
                {''.join(cand_rows)}
              </tbody>
            </table>
          </div>
        </section>""")

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>TermMatchAI - User to FAIRe mapping</title>
  <style>
    :root {{
      --bg: #f3f6f4;
      --ink: #1a2421;
      --muted: #5c6b66;
      --card: #ffffff;
      --line: #d5ddd9;
      --accent: #0f6b5c;
      --accent-soft: #d8efe9;
      --exact: #1b7f4e;
      --normalized: #2a6f97;
      --fuzzy: #a65d1a;
      --semantic: #0f6b5c;
      --unmatched: #8a4b4b;
      --bar: #0f6b5c;
      --shadow: 0 1px 2px rgba(26, 36, 33, 0.06), 0 8px 24px rgba(26, 36, 33, 0.06);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: "IBM Plex Sans", "Segoe UI", sans-serif;
      color: var(--ink);
      background:
        radial-gradient(1200px 500px at 10% -10%, #e4f2ee 0%, transparent 55%),
        radial-gradient(900px 400px at 100% 0%, #e8ebe4 0%, transparent 50%),
        var(--bg);
      line-height: 1.45;
    }}
    h1, h2, h3 {{
      font-family: "IBM Plex Serif", Georgia, serif;
      font-weight: 600;
      letter-spacing: -0.02em;
    }}
    .wrap {{ max-width: 1100px; margin: 0 auto; padding: 2rem 1.25rem 4rem; }}
    header.hero {{
      margin-bottom: 2rem;
      padding-bottom: 1.25rem;
      border-bottom: 1px solid var(--line);
    }}
    header.hero h1 {{ margin: 0 0 0.35rem; font-size: 1.9rem; }}
    header.hero p {{ margin: 0; color: var(--muted); max-width: 42rem; }}
    .stats {{
      display: flex; flex-wrap: wrap; gap: 0.6rem;
      margin: 1.25rem 0 0;
    }}
    .stat {{
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 0.35rem 0.85rem;
      font-size: 0.9rem;
      box-shadow: var(--shadow);
    }}
    .stat strong {{ color: var(--accent); }}
    section.block {{
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: 12px;
      box-shadow: var(--shadow);
      padding: 1.25rem 1.35rem 1.5rem;
      margin-bottom: 1.75rem;
    }}
    section.block > h2 {{ margin: 0 0 0.35rem; font-size: 1.25rem; }}
    section.block > .lede {{ margin: 0 0 1rem; color: var(--muted); font-size: 0.95rem; }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.92rem;
    }}
    th, td {{
      text-align: left;
      padding: 0.65rem 0.55rem;
      border-bottom: 1px solid var(--line);
      vertical-align: top;
    }}
    th {{
      font-size: 0.75rem;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      color: var(--muted);
      font-weight: 600;
    }}
    tr:last-child td {{ border-bottom: none; }}
    code {{
      font-family: "IBM Plex Mono", Consolas, monospace;
      font-size: 0.88em;
      background: var(--accent-soft);
      padding: 0.1rem 0.35rem;
      border-radius: 4px;
    }}
    a {{ color: var(--accent); text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    .badge {{
      display: inline-block;
      font-size: 0.75rem;
      font-weight: 600;
      padding: 0.2rem 0.55rem;
      border-radius: 999px;
      white-space: nowrap;
    }}
    .badge-exact {{ background: #d9f2e4; color: var(--exact); }}
    .badge-normalized {{ background: #dcecf7; color: var(--normalized); }}
    .badge-fuzzy {{ background: #fce8d4; color: var(--fuzzy); }}
    .badge-semantic {{ background: var(--accent-soft); color: var(--semantic); }}
    .badge-unmatched {{ background: #f5e0e0; color: var(--unmatched); }}
    .score-cell {{
      min-width: 7.5rem;
      white-space: nowrap;
    }}
    .score-bar-wrap {{
      display: inline-block;
      width: 4.5rem;
      height: 0.45rem;
      background: #e4ebe8;
      border-radius: 999px;
      overflow: hidden;
      vertical-align: middle;
      margin-right: 0.4rem;
    }}
    .score-bar {{
      height: 100%;
      background: var(--bar);
      border-radius: 999px;
    }}
    .score-num {{ font-variant-numeric: tabular-nums; font-weight: 600; font-size: 0.88rem; }}
    .field-card {{
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: 12px;
      box-shadow: var(--shadow);
      margin-bottom: 1rem;
      overflow: hidden;
    }}
    .field-card > header {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 1rem;
      padding: 0.85rem 1.15rem;
      background: #f7faf8;
      border-bottom: 1px solid var(--line);
    }}
    .field-card > header h3 {{ margin: 0; font-size: 1.05rem; font-family: "IBM Plex Sans", sans-serif; }}
    .field-body {{ padding: 1rem 1.15rem 1.15rem; }}
    .field-body .desc {{ margin: 0 0 0.5rem; color: var(--muted); }}
    .field-body .example {{ margin: 0 0 1rem; }}
    .candidates .meta {{ margin: 0.15rem 0; }}
    .muted {{ color: var(--muted); font-size: 0.88rem; }}
    footer.note {{
      margin-top: 2rem;
      color: var(--muted);
      font-size: 0.88rem;
    }}
    @media (max-width: 720px) {{
      .score-bar-wrap {{ display: none; }}
      th:nth-child(4), td:nth-child(4) {{ display: none; }}
      .candidates th:nth-child(4), .candidates td:nth-child(4) {{ display: table-cell; }}
    }}
  </style>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@400;600&family=IBM+Plex+Serif:wght@600&display=swap" rel="stylesheet" />
</head>
<body>
  <div class="wrap">
    <header class="hero">
      <h1>Your fields to FAIRe</h1>
      <p>
        Each row is a field from your data standard, mapped to the closest FAIRe eDNA term(s).
        Scores show how confident the match is. Click a field name to jump to its full candidate list.
      </p>
      <div class="stats">
        <div class="stat"><strong>{len(rows)}</strong> user fields</div>
        <div class="stat"><strong>{n_exact}</strong> exact</div>
        <div class="stat"><strong>{n_norm}</strong> normalized</div>
        <div class="stat"><strong>{n_fuzzy}</strong> fuzzy</div>
        <div class="stat"><strong>{n_sem}</strong> semantic</div>
        <div class="stat"><strong>{n_none}</strong> unmatched</div>
      </div>
    </header>

    <section class="block" id="summary">
      <h2>Summary</h2>
      <p class="lede">Best match for every user field. Same scores as in the detail cards below.</p>
      <table>
        <thead>
          <tr>
            <th>Your field</th>
            <th>Best FAIRe match</th>
            <th>How matched</th>
            <th>Score</th>
          </tr>
        </thead>
        <tbody>
          {''.join(summary_rows_html)}
        </tbody>
      </table>
    </section>

    <section class="block" id="details" style="background:transparent;border:none;box-shadow:none;padding:0;">
      <h2 style="margin-bottom:0.35rem;">Field by field</h2>
      <p class="lede" style="margin-bottom:1rem;">All suggested FAIRe matches for each of your fields (up to {num_matches} for semantic matches).</p>
      {''.join(detail_blocks_html)}
    </section>

    <footer class="note">
      Exact / normalized = name match (shown as 100%).
      Fuzzy = string similarity (0-100).
      Semantic = SciBERT similarity on field name + description + example value (shown as %).
      Semantic threshold used: {bert_threshold:.2f} ({bert_threshold * 100:.0f}%).
    </footer>
  </div>
</body>
</html>
"""

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(page)

    return output_file
