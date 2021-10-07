#!/usr/bin/env -S bash -euET -o pipefail -O inherit_errexit
SCRIPT=$(readlink -f "$0") && cd $(dirname "$SCRIPT")

# --- Script Init ---

mkdir -p log
rm -R -f log/*

# --- Setup run dirs ---

find output -type f -not -name '*summary-info*' -not -name '*.json' -exec rm -R -f {} +

rm -R -f fifo/*
rm -R -f work/*
mkdir work/kat/

mkdir work/il_S1_summaryaalcalc

mkfifo fifo/il_P16

mkfifo fifo/il_S1_summary_P16



# --- Do insured loss computes ---
tee < fifo/il_S1_summary_P16 work/il_S1_summaryaalcalc/P16.bin > /dev/null & pid1=$!
summarycalc -m -f  -1 fifo/il_S1_summary_P16 < fifo/il_P16 &

eve -R 16 20 | getmodel | gulcalc -S100 -L100 -r -a0 -i - | fmcalc -a2 > fifo/il_P16  &

wait $pid1


# --- Do insured loss kats ---
