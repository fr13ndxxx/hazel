import ast

class Validator:
    def __init__(self, rules):
        self.rules = rules

    def validate(self, dataframe):
        errors = []
        for index, row in dataframe.iterrows():
            for field, rule in self.rules.items():
                if field in row:
                    value = row[field]
                    # Apply rule based on type
                    if rule['type'] == 'ЦЕЛОЕ':
                        if 'min' in rule and int(value) < rule['min']:
                            errors.append((index, field, value, rule))
                        elif 'max' in rule and int(value) > rule['max']:
                            errors.append((index, field, value, rule))
                    elif rule['type'] == 'ВЕЩЕСТВЕННОЕ':
                        if 'min' in rule and float(value) < rule['min']:
                            errors.append((index, field, value, rule))
                        elif 'max' in rule and float(value) > rule['max']:
                            errors.append((index, field, value, rule))
                    elif rule['type'] == 'СТРОКА':
                        if 'max_length' in rule and len(value) > rule['max_length']:
                            errors.append((index, field, value, rule))
                        elif 'allowed_chars' in rule:
                            for char in value:
                                if char not in rule['allowed_chars']:
                                    errors.append((index, field, value, rule))
                        elif 'date_format' in rule:
                            try:
                                ast.parse(value, rule['date_format'])
                            except SyntaxError:
                                errors.append((index, field, value, rule))
                    # Add more rule types as needed
        return errors

    def apply_rule(self, value, rule):
        # Example rule application
        if rule['type'] == 'INTEGER':
            return self.validate_integer(value, rule)
        elif rule['type'] == 'FLOAT':
            return self.validate_float(value, rule)
        elif rule['type'] == 'STRING':
            return self.validate_string(value, rule)
        # Add more rule types as needed
        return True

    def validate_integer(self, value, rule):
        try:
            int_value = int(value)
            if 'min' in rule and int_value < rule['min']:
                return False
            if 'max' in rule and int_value > rule['max']:
                return False
            return True
        except ValueError:
            return False

    def validate_float(self, value, rule):
        try:
            float_value = float(value)
            if 'min' in rule and float_value < rule['min']:
                return False
            if 'max' in rule and float_value > rule['max']:
                return False
            return True
        except ValueError:
            return False

    def validate_string(self, value, rule):
        if 'max_length' in rule and len(value) > rule['max_length']:
            return False
        if 'allowed_chars' in rule:
            for char in value:
                if char not in rule['allowed_chars']:
                    return False
        return True
