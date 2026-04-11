import originpro as op

# Column formulas require letters instead of column indices
def col_index_to_letter(idx):
    letters = ""
    idx += 1  # convert to 1-based
    while idx > 0:
        idx, rem = divmod(idx - 1, 26)
        letters = chr(65 + rem) + letters
    return letters


wks = op.find_sheet()

# number of phase columns imported
n_phases = wks.cols - 1
wks.cols = 2+4*n_phases

wks._user_param_row('Norm Type',True)
frac_idx = wks._user_param_row('Phase Fraction',True)+1

source_range = f'{col_index_to_letter(1)}1:{col_index_to_letter(n_phases)}0'
phase_range = f'{col_index_to_letter(1+n_phases)}1:{col_index_to_letter(2*n_phases)}0'
max_norm_range = f'{col_index_to_letter(1+2*n_phases)}:{col_index_to_letter(3*n_phases)}'
sum_norm_range =f'{col_index_to_letter(1+3*n_phases)}:{col_index_to_letter(4*n_phases)}'

copy_labels = ['L','U','SourceFile']

sum_col = wks.cols-1
wks.set_label(sum_col,'Normalized','Norm Type')
sum_formula = f'sum({sum_norm_range})'
wks.set_formula(sum_col,sum_formula)
wks.set_label(sum_col,'Int','L')
wks.set_label(sum_col, 'AU','U')
wks.set_label(sum_col,'All Phases','C')

for col in range(1,n_phases+1):
    wks.set_label(col,'Non-normalized','Norm Type')

    phase_col = col+n_phases
    wks.set_label(phase_col,'Phase-scaled','Norm Type')
    wks.set_label(phase_col,1.0,'Phase Fraction')

    source_letter = col_index_to_letter(col)
    phase_formula = f'{source_letter} * This[D{frac_idx}] / max({source_range})'
    wks.set_formula(phase_col,phase_formula)

    max_norm_col = phase_col+n_phases
    wks.set_label(max_norm_col,'Max=1','Norm Type')

    phase_letter = col_index_to_letter(phase_col)
    max_norm_formula = f'{phase_letter} / max({phase_range})'
    wks.set_formula(max_norm_col,max_norm_formula)

    sum_norm_col = max_norm_col+n_phases
    wks.set_label(sum_norm_col,'Sum=1','Norm Type')
    
    max_norm_letter = col_index_to_letter(max_norm_col)
    sum_norm_formula = f'{max_norm_letter} / max(sum({max_norm_range}))'
    wks.set_formula(sum_norm_col,sum_norm_formula)


    for lbl in copy_labels:
        val = wks.get_label(col,lbl)
        if val:
            for calc_col in (phase_col,max_norm_col,sum_norm_col):
                wks.set_label(calc_col,val,lbl)






