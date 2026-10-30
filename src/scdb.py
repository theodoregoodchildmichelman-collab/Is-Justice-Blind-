"""Load the Supreme Court Database (SCDB) into one row per justice per case.

Download source: http://scdb.wustl.edu/data.php, release 2026_01 (terms 1946-2025).
Codebook: http://scdb.wustl.edu/documentation.php
"""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
JUSTICE_FILE = ROOT / "data/raw/scdb/SCDB_2026_01_justiceCentered_Citation.csv"

# decisionType codes for cases that were orally argued and decided on the merits:
# 1 = signed opinion, 6 = per curiam after argument, 7 = judgment of the Court.
ARGUED_DECISION_TYPES = [1, 6, 7]


def load_votes() -> pd.DataFrame:
    """One row per (case, justice) for argued merits cases, with clean 0/1 columns.

    Columns added:
      petitioner_won   1 if the petitioner won the case (roughly "reversed"), else 0
      voted_petitioner 1 if this justice voted for the petitioner's side
      voted_conserv    1 if this justice's vote was in the conservative direction
      lc_conserv       1 if the lower-court ruling under review was conservative,
                       0 if liberal, NaN if SCDB could not code it
    """
    df = pd.read_csv(JUSTICE_FILE, encoding="latin-1", low_memory=False)
    df = df[df.decisionType.isin(ARGUED_DECISION_TYPES)]

    # Drop cases where the winner is unclear (partyWinning == 2) or votes are missing.
    df = df[df.partyWinning.isin([0, 1]) & df.majority.isin([1, 2])].copy()

    df["petitioner_won"] = df.partyWinning.astype(int)
    in_majority = (df.majority == 2).astype(int)
    # A justice in the majority voted with the winner; a dissenter voted against.
    df["voted_petitioner"] = (in_majority == df.petitioner_won).astype(int)
    # SCDB direction: 1 = conservative, 2 = liberal.
    df["voted_conserv"] = df.direction.map({1: 1, 2: 0})
    df["lc_conserv"] = df.lcDispositionDirection.map({1: 1, 2: 0})
    return df
