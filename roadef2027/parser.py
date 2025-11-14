import re
from typing import List, Dict
from .models import Technician, Intervention


def parse_bracketed_list(s: str) -> List[int]:
    s = s.strip()
    if s == "[]" or s == "[ ]":
        return []
    # find all integers inside brackets (allow negative just in case)
    return list(map(int, re.findall(r"-?\d+", s)))


def parse_instance_file(path: str):
    with open(path, "r") as f:
        # read non-empty lines
        lines = [ln.strip() for ln in f if ln.strip()]
        if not lines:
            raise ValueError(f"Empty instance file: {path}")
        # detect header: if first non-empty line contains any non-numeric token (besides the name), treat it as a header
        first_tokens = lines[0].split()
        data_line = None
        if len(first_tokens) >= 6 and all(tok.lstrip("-").isdigit() for tok in first_tokens[1:6]):
            # first line already looks like data (name followed by 5 numeric fields)
            data_line = lines[0]
        else:
            # header present; use next non-empty line as data
            if len(lines) < 2:
                raise ValueError(f"No data line found in instance file after header: {path}")
            data_line = lines[1]
        parts = data_line.split()
        name = parts[0]
        n_domains, n_levels, n_techs, n_interv, abandon_cost = map(int, parts[1:6])
        return name, n_domains, n_levels, n_techs, n_interv, abandon_cost


def parse_interv_list(path: str, n_domains: int, n_levels: int) -> List[Intervention]:
    interventions = []
    # helper to keep bracketed lists like '[ ]' or '[1 2]' as a single token
    def _tokenize_line(line: str):
        return re.findall(r"\[.*?\]|\S+", line)

    with open(path, "r") as f:
        it = iter(f)
        # skip header lines until we find the first data row (first token starts with a digit or a minus)
        for line in it:
            parts = _tokenize_line(line.strip())
            if not parts:
                continue
            if parts[0].lstrip("-").isdigit():
                # this is the first data line; process it and then continue with the rest
                first_data_lines = [line]
                break
        else:
            # no data rows
            return interventions

        # process the first data line and the rest of the iterator
        for line in first_data_lines + list(it):
            parts = _tokenize_line(line.strip())
            if not parts:
                continue
            iid = int(parts[0])
            duration = int(parts[1])
            preds = parse_bracketed_list(parts[2])
            priority = int(parts[3])
            cost = int(parts[4])
            req_flat = list(map(int, parts[5 : 5 + n_domains * n_levels]))
            requirements: Dict[int, Dict[int, int]] = {}
            idx = 0
            for d in range(1, n_domains + 1):
                requirements[d] = {}
                for l in range(1, n_levels + 1):
                    requirements[d][l] = req_flat[idx]
                    idx += 1
            interventions.append(
                Intervention(iid, duration, preds, priority, cost, requirements)
            )
    return interventions


def parse_tech_list(path: str, n_domains: int) -> List[Technician]:
    techs = []
    def _tokenize_line(line: str):
        return re.findall(r"\[.*?\]|\S+", line)

    with open(path, "r") as f:
        it = iter(f)
        # skip header lines until we find the first data row
        for line in it:
            parts = _tokenize_line(line.strip())
            if not parts:
                continue
            if parts[0].lstrip("-").isdigit():
                first_data_lines = [line]
                break
        else:
            return techs

        for line in first_data_lines + list(it):
            parts = _tokenize_line(line.strip())
            if not parts:
                continue
            tid = int(parts[0])
            levels = {d + 1: int(parts[1 + d]) for d in range(n_domains)}
            dispo = []
            if len(parts) > n_domains + 1:
                dispo = parse_bracketed_list(parts[n_domains + 1])
            techs.append(Technician(tid, levels, dispo))
    return techs
