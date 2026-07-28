from pathlib import Path
import webbrowser

from data_loading.data_loading import (
    get_terms_with_data,
    FAIRE_STANDARD_PATH,
    USER_STANDARD_EXAMPLE_PATH,
)
from core.normalization import normalize
from core.matching import normalized_match, exact_match
from core.fuzzy_matching import fuzzy_match
# from ai_matching.semantic_matching_spacy import find_semantic_matches_spacy
from ai_matching.semantic_matching_BERT import find_semantic_matches_scibert
from core.generate_report import generate_report
from cli_ui import (
    console,
    quiet_third_party_logs,
    print_banner,
    list_input_jsons,
    prompt_choose_input_json,
    prompt_num_matches,
    default_index_for,
    step,
    step_done,
)


def main():
    quiet_third_party_logs()
    print_banner()

    input_files = list_input_jsons()
    faire_path = prompt_choose_input_json(
        "Match TO — FAIRe / template standard",
        input_files,
        default_index=default_index_for(input_files, Path(FAIRE_STANDARD_PATH).name),
        show_menu=True,
    )
    user_path = prompt_choose_input_json(
        "Match FROM — your / other data standard",
        input_files,
        default_index=default_index_for(
            input_files, Path(USER_STANDARD_EXAMPLE_PATH).name
        ),
        show_menu=False,
    )
    num_matches = prompt_num_matches(default=3)

    console.print("[bold]Loading standards...[/bold]")
    template_terms_w_data, user_terms_w_data = get_terms_with_data(
        faire_path=str(faire_path),
        user_path=str(user_path),
    )
    step_done(
        f"Loaded {len(user_terms_w_data)} user fields → "
        f"{len(template_terms_w_data)} FAIRe fields"
    )
    console.print()

    remaining_user_terms = dict(user_terms_w_data)
    remaining_template_terms = dict(template_terms_w_data)

    # Exact matching against template terms
    step("Exact matching...")
    exact_matches = exact_match(
        list(remaining_template_terms.keys()), list(remaining_user_terms.keys())
    )
    remaining_user_terms = {
        term: data
        for term, data in remaining_user_terms.items()
        if term not in exact_matches
    }
    step_done(f"Exact: {len(exact_matches)} matches")

    # Normalize terms
    normalized_template_terms = [
        normalize(term) for term in remaining_template_terms.keys()
    ]
    normalized_user_terms = [normalize(term) for term in remaining_user_terms.keys()]

    # Normalized matching against template terms
    step("Normalized matching...")
    normalized_matches = normalized_match(
        normalized_template_terms, normalized_user_terms
    )
    remaining_user_terms = {
        term: data
        for term, data in remaining_user_terms.items()
        if normalize(term) not in normalized_matches
    }
    step_done(f"Normalized: {len(normalized_matches)} matches")

    # Fuzzy matching against template terms
    # fuzzy_match returns {norm_template: (norm_user, score)}; invert for user-side removal
    step("Fuzzy matching...")
    fuzzy_matches = fuzzy_match(
        normalized_template_terms,
        [normalize(term) for term in remaining_user_terms],
    )
    fuzzy_user_norms = {norm_user for norm_user, _ in fuzzy_matches.values()}
    remaining_user_terms = {
        term: data
        for term, data in remaining_user_terms.items()
        if normalize(term) not in fuzzy_user_norms
    }
    step_done(f"Fuzzy: {len(fuzzy_matches)} matches")

    # Semantic matching (description embeddings + light name-token blend)
    remaining_count = len(remaining_user_terms)
    step(f"Semantic matching ({remaining_count} remaining fields)...")
    with console.status(
        "[bold cyan]Running semantic matching (may download model on first run)...[/]",
        spinner="dots",
    ):
        semantic_matches_scibert = find_semantic_matches_scibert(
            remaining_user_terms,
            remaining_template_terms,
            num_matches=num_matches,
            quiet=True,
        )
    step_done(f"Semantic: {len(semantic_matches_scibert)} fields scored")

    # Identify new terms
    new_terms = list(remaining_user_terms.keys())

    # Generate report
    step("Writing HTML report...")
    report_path = generate_report(
        normalized_matches,
        exact_matches,
        semantic_matches_scibert,
        new_terms,
        'term_matching_report.html',
        user_terms_w_data,
        template_terms_w_data,
        bert_threshold=0.3,
        num_matches=num_matches,
        fuzzy_matches=fuzzy_matches,
    )
    step_done(f"Report: {report_path}")
    console.print()
    console.print("[bold green]Done.[/bold green] Opening report in your browser.")
    webbrowser.open(Path(report_path).resolve().as_uri())


if __name__ == '__main__':
    main()
