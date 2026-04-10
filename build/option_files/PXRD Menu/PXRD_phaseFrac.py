import originpro as op
import sys

def lt_start(file_mode,param_mode):
    lt_cmd = f'''
        run -pyf PXRD_cifPicker.py "{file_mode}";
        run -pyf PXRD_cifImp.py "{param_mode}" "false";
    '''
    return lt_cmd


if __name__ == "__main__":
    file_mode = sys.argv[1] if len(sys.argv) > 1 else "file"
    param_mode = sys.argv[2] if len(sys.argv) > 2 else "CuKa"

    op.lt_exec(lt_start(file_mode,param_mode))

