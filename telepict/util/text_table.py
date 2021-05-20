from collections import defaultdict

def ascii_table(l, header_rows=1, sep='|', align='<', stringify_func=repr):
    max_col_widths = defaultdict(int)
    num_cols = 0
    for row in l:
        num_cols = max(num_cols, len(row))
        for col_i, element in enumerate(row):
            formatted = row[col_i] = stringify_func(element) if not isinstance(element, str) else element
            max_col_widths[col_i] = max(max_col_widths[col_i], len(formatted))

    col_widths = [max_col_widths[i] for i in range(num_cols)]
    row_width = sum(col_widths) + len(sep) * (num_cols - 1)
    if len(align) == 1:
        align = align * num_cols
    elif len(align) != num_cols:
        raise ValueError(f'Align string {align} does not match number of columns {num_cols}')

    formatted_l = list()

    for row in l:
        formatted_row = list()
        for col_i, element in enumerate(row):
            align_c = align[col_i]
            formatted = f'{element:{align_c}{col_widths[col_i]}}'
            formatted_row.append(formatted)
        formatted_l.append(sep.join(formatted_row))

    if header_rows:
        formatted_l.insert(header_rows, '-' * row_width)
    
    return '\n'.join(formatted_l)
