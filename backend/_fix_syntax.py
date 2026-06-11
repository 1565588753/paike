import pathlib, re

USER_CANONICAL = 'user: User = Depends(RoleRequired(["admin", "academic"]))'

def parse_params(params_str):
    parts = []
    depth = 0
    buf = ''
    for ch in params_str:
        if ch == '(': depth += 1
        elif ch == ')': depth -= 1
        if ch == ',' and depth == 0:
            if buf.strip(): parts.append(buf.strip())
            buf = ''
        else:
            buf += ch
    if buf.strip(): parts.append(buf.strip())
    return parts


def fix_file(path):
    lines = path.read_text().split('\n')
    new_lines = list(lines)
    i = 0
    while i < len(new_lines):
        line = new_lines[i]
        if 'def ' in line and 'RoleRequired' not in line:
            sig_lines = [line]
            balance = line.count('(') - line.count(')')
            j = i + 1
            while j < len(new_lines) and balance > 0:
                sig_lines.append(new_lines[j])
                balance += new_lines[j].count('(') - new_lines[j].count(')')
                j += 1
            if balance == 0:
                combined = ' '.join(s.strip() for s in sig_lines)
                if 'RoleRequired' in combined and 'admin' in combined:
                    m = re.match(r'(\s*)def\s+(\w+)\s*\((.*)\):\s*$', combined)
                    if m:
                        indent, fname, params_str = m.group(1), m.group(2), m.group(3)
                        parts = parse_params(params_str)
                        # Normalize user param
                        user_idx = None
                        new_parts = []
                        for idx, p in enumerate(parts):
                            if 'user:' in p and 'RoleRequired' in p:
                                new_parts.append(USER_CANONICAL)
                                user_idx = idx
                            else:
                                new_parts.append(p)
                        if user_idx is None:
                            i += 1
                            continue
                        # Build new signature
                        param_indent = indent + '    '
                        new_sig = [indent + 'def ' + fname + '(']
                        for p in new_parts[:user_idx]:
                            new_sig.append(param_indent + p + ',')
                        new_sig.append(param_indent + USER_CANONICAL + '):')
                        # Replace
                        new_lines[i:j] = new_sig
                        i = i + len(new_sig) - 1
        elif 'def ' in line and 'RoleRequired' in line:
            m = re.match(r'(\s*)def\s+(\w+)\s*\((.*)\):\s*$', line.strip() and line)
            # treat similarly above... but we need more lines
            # simplest: treat like the previous case
            sig_lines = [line]
            balance = line.count('(') - line.count(')')
            j = i + 1
            while j < len(new_lines) and balance > 0:
                sig_lines.append(new_lines[j])
                balance += new_lines[j].count('(') - new_lines[j].count(')')
                j += 1
            if balance == 0:
                combined = ' '.join(s.strip() for s in sig_lines)
                m2 = re.match(r'(\s*)def\s+(\w+)\s*\((.*)\):\s*$', combined)
                if m2:
                    indent, fname, params_str = m2.group(1), m2.group(2), m2.group(3)
                    parts = parse_params(params_str)
                    user_idx = None
                    new_parts = []
                    for idx, p in enumerate(parts):
                        if 'user:' in p and 'RoleRequired' in p:
                            new_parts.append(USER_CANONICAL)
                            user_idx = idx
                        else:
                            new_parts.append(p)
                    if user_idx is None:
                        i += 1
                        continue
                    param_indent = indent + '    '
                    new_sig = [indent + 'def ' + fname + '(']
                    for p in new_parts[:user_idx]:
                        new_sig.append(param_indent + p + ',')
                    new_sig.append(param_indent + USER_CANONICAL + '):')
                    new_lines[i:j] = new_sig
                    i = i + len(new_sig) - 1
        i += 1
    path.write_text('\n'.join(new_lines))


if __name__ == '__main__':
    for p in pathlib.Path('app/api/v1/endpoints').glob('*.py'):
        fix_file(p)
    # Verify
    import ast
    for p in pathlib.Path('app/api/v1/endpoints').glob('*.py'):
        try:
            ast.parse(p.read_text())
            print(f'{p.name}: OK')
        except SyntaxError as e:
            print(f'{p.name}: line {e.lineno}: {e.msg}')
