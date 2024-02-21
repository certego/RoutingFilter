from dataclasses import dataclass


@dataclass
class Results:
    rules: str
    output: dict

    def __init__(self, rules, output):
        self.rules = rules
        self.output = output["customer"] if output is not None and "customer" in output.keys() else output

    def to_dict(self):
        return {"output": self.output, "rules": self.rules}
