from dataclasses import dataclass


@dataclass
class Results:
    rules: str
    output: dict | None

    def __init__(self, rules: str, output: dict | None):
        self.rules = rules
        self.output = output["customer"] if output is not None and "customer" in output.keys() else output

    def to_dict(self) -> dict:
        return {"output": self.output, "rules": self.rules}
