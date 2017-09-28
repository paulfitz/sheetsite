import daff
import json
import os
import uuid


def process_ids(prev_file, curr_file, prev_id_file, id_file):
    io = daff.TableIO()
    dapp = daff.Coopy(io)
    if not os.path.exists(prev_file):
        prev_file = curr_file
    v1 = dapp.loadTable(prev_file)
    v2 = dapp.loadTable(curr_file)
    flags = daff.CompareFlags()
    flags.allow_nested_cells = True
    alignment = daff.compareTables3(None, v1, v2, flags).align()
    daff.TableDiff(alignment, flags).hiliteSingle(daff.SimpleTable(0, 0))
    if os.path.exists(prev_id_file):
        in_refs = json.load(open(prev_id_file))
    else:
        in_refs = {}
    out_refs = {}
    for part in alignment.comp.child_order:
        comp = alignment.comp.children.get(part)
        nalignment = comp.alignment
        order = nalignment.toOrder().getList()
        v1 = comp.a
        v2 = comp.b
        ref = in_refs.get(part, {})
        if part not in out_refs:
            out_ref = out_refs[part] = {}
        mints = 0
        copies = 0
        drops = 0
        for o in order:
            if o.r == 0:
                continue
            if o.r >= 0 and o.l >= 0:
                src = ref.get(str(o.l))
                if src is None:
                    out_ref[o.r] = str(uuid.uuid4())
                    mints += 1
                else:
                    out_ref[o.r] = ref[str(o.l)]
                    copies += 1
            if o.r < 0 and o.l >= 0:
                drops += 1
            if o.r >= 0 and o.l < 0:
                out_ref[o.r] = str(uuid.uuid4())
                mints += 1
    json.dump(out_refs, open(id_file, 'w'), indent=2)
    return out_refs
