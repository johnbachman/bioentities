import csv
import sys


def _read_csv(fh, delimiter, quotechar):
    if sys.version_info.major < 3:
        csvreader = csv.reader(fh, delimiter=bytes(delimiter),
                               quotechar=bytes(quotechar))
        rows = [[cell.decode('utf-8') for cell in row] for row in csvreader]
    else:
        csvreader = csv.reader(fh, delimiter=delimiter, quotechar=quotechar)
        rows = [row for row in csvreader]
    return rows


def load_csv(filename):
    """Load famplex csv file as list of rows

    Parameters
    ----------
    filename : str

    Returns
    -------
    rows : list
    """
    with open(filename) as f:
        csvreader = csv.reader(f, delimiter=str(u','),
                               lineterminator='\r\n',
                               quoting=csv.QUOTE_MINIMAL,
                               quotechar=str(u'"'))
        rows = [row for row in csvreader]
    return rows


def construct_grounding_map(rows):
    """Construct grounding map from rows in a grounding_map csv file

    Parameters
    ----------
    rows : list
        List of rows from a grounding map csv file. File should contain seven
        columns, the first of which is a Famplex ID. The remaining columns
        contain namespace, id pairs, each pair occupying two columns. Some
        columns may be blank but file must be padded out with commas.

    Returns
    -------
    gmap : dict
        Dictionary mapping Famplex IDs to INDRA style db_refs dicts. Each
        db_refs dict maps namespaces to ids.
    """
    gmap = {}
    for row in rows:
        text = row[0]
        db_refs = {'TEXT': text}
        db_refs.update({ns: id_ for ns, id_ in zip(row[1::2], row[2::2])})
        gmap[text] = db_refs if len(db_refs) > 1 else None
    return gmap


def update_id_prefixes(filename):
    """Return list of rows in grounding map with IDs corrected

    Parameters
    ----------
    filename : str
        Location of a grounding map csv file

    Returns
    -------
    list
        List of rows from input with GO, CHEBI, and CHEMBL IDs
        corrected to be prefixed with the namespace.
    """
    gm_rows = load_csv(filename)
    updated_rows = []
    for row in gm_rows:
        key = row[0]
        keys = [entry for entry in row[1::2]]
        values = [entry for entry in row[2::2]]
        if 'GO' in keys:
            go_ix = keys.index('GO')
            values[go_ix] = 'GO:%s' % values[go_ix]
        if 'CHEBI' in keys:
            chebi_ix = keys.index('CHEBI')
            values[chebi_ix] = 'CHEBI:%s' % values[chebi_ix]
        if 'CHEMBL' in keys:
            chembl_ix = keys.index('CHEMBL')
            values[chembl_ix] = 'CHEMBL%s' % values[chembl_ix]
        updated_row = [key]
        for pair in zip(keys, values):
            updated_row += pair
        updated_rows.append(updated_row)
    return updated_rows


