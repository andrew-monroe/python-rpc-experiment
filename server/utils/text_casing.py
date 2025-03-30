import re

def to_snake_case(string):
    # Insert underscore before uppercase letters and convert to lowercase
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', string)
    s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
    # Replace spaces and hyphens with underscores
    s3 = s2.lower().replace(' ', '_').replace('-', '_')
    # Remove consecutive underscores
    return re.sub('_+', '_', s3)

def to_kebab_case(string):
    # Insert hyphen before uppercase letters and convert to lowercase
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1-\2', string)
    s2 = re.sub('([a-z0-9])([A-Z])', r'\1-\2', s1)
    # Replace spaces and underscores with hyphens
    s3 = s2.lower().replace(' ', '-').replace('_', '-')
    # Remove consecutive hyphens
    return re.sub('-+', '-', s3)
