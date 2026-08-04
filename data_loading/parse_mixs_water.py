"""
Parse the MIxS Water environmental extension into TermMatchAI JSON.

Only slots belonging to the MIxS Water class (MIXS:0016014), including its
inherited slots, are exported. This keeps unrelated environmental packages
out while retaining general required terms used by Water.

Usage:
  python data_loading/parse_mixs_water.py
  python data_loading/parse_mixs_water.py path/to/mixs.yaml path/to/output.json
"""

import json
import os
import sys

import yaml


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_SCHEMA_PATH = os.path.join(REPO_ROOT, 'script_dependencies', 'mixs.yaml')
DEFAULT_OUTPUT_PATH = os.path.join(REPO_ROOT, 'inputs', 'MIxS_water_standard.json')
WATER_CLASS = 'Water'


def _class_slots(classes, class_name, visited=None):
    """Return slots declared by a class and its ancestors, without duplicates."""
    visited = visited or set()
    if class_name in visited:
        raise ValueError(f'Circular MIxS class inheritance involving {class_name}')
    if class_name not in classes:
        raise KeyError(f'MIxS class not found: {class_name}')

    visited.add(class_name)
    class_definition = classes[class_name] or {}
    slot_names = []

    parent_name = class_definition.get('is_a')
    if parent_name:
        slot_names.extend(_class_slots(classes, parent_name, visited))

    slot_names.extend(class_definition.get('slots') or [])
    visited.remove(class_name)
    return list(dict.fromkeys(slot_names))


def _first_example(slot_definition):
    """Return the first LinkML example value, or null when none is supplied."""
    examples = slot_definition.get('examples') or []
    if not examples:
        return None

    example = examples[0]
    if isinstance(example, dict):
        return example.get('value')
    return example


def parse_mixs_water(schema_path):
    """
    Return Water slot names mapped to TermMatchAI value/description entries.

    Class-specific examples override general slot examples, as required by
    LinkML slot_usage semantics.
    """
    with open(schema_path, 'r', encoding='utf-8') as schema_file:
        schema = yaml.safe_load(schema_file)

    classes = schema.get('classes') or {}
    slots = schema.get('slots') or {}
    water_definition = classes.get(WATER_CLASS)
    if water_definition is None:
        raise KeyError(f'MIxS class not found: {WATER_CLASS}')

    water_slot_usage = water_definition.get('slot_usage') or {}
    terms = {}

    for slot_name in _class_slots(classes, WATER_CLASS):
        if slot_name not in slots:
            raise KeyError(f'MIxS slot not found: {slot_name}')

        slot_definition = slots[slot_name] or {}
        class_override = water_slot_usage.get(slot_name) or {}
        example_source = (
            class_override if class_override.get('examples') else slot_definition
        )

        terms[slot_name] = {
            'value': _first_example(example_source),
            'description': slot_definition.get('description') or ''
        }

    return terms


def write_mixs_water_json(terms, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as output_file:
        json.dump(terms, output_file, indent=2, ensure_ascii=False, default=str)
        output_file.write('\n')


def main():
    schema_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_SCHEMA_PATH
    output_path = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_OUTPUT_PATH

    if not os.path.isfile(schema_path):
        raise FileNotFoundError(f'MIxS schema not found: {schema_path}')

    terms = parse_mixs_water(schema_path)
    write_mixs_water_json(terms, output_path)
    print(f'Wrote {len(terms)} MIxS Water terms to {output_path}')


if __name__ == '__main__':
    main()
