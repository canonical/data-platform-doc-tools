# Converts prometheus alert rules to a markdown-formatted table containing the alert name, severity, and description.
import yaml

rule_file = 'mysql_rules.yaml'
output_file = 'output.md'

def group_to_table(group):
    name = group['name']
    rules = group['rules']

    text = f"## {name}\n\n"
    text += "| Alert | Severity | Notes |\n"
    text += "|------|----------|-------|\n"

    for rule in rules:
        alert = rule['alert'].strip()
        severity = rule['labels']['severity'].strip()
        description = rule['annotations']['summary'].strip() + '<br>' + rule['annotations']['description'].strip()
        description = description.replace("{{ $labels.instance }}", "")
        description = description.replace("LABELS = {{ $labels }}.", "")
        description = description.replace('\n', '')

        text += f"| {alert} | `{severity}` | {description} |\n"

    return text.replace("\n |", "")

with open(rule_file, 'r') as f:
    data = yaml.load(f, Loader=yaml.SafeLoader)

groups = data['groups']
for group in groups:
    text += group_to_table(group)
    text += '\n'

text = text.replace("\n |", "")
with open(output_file, "w") as file:
    file.write(text)
