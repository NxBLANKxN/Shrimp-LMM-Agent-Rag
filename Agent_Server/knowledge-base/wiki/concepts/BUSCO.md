# BUSCO

**BUSCO** (Benchmarking Universal Single-Copy Orthologs) is a tool used to assess the completeness of a genome or transcriptome assembly. It works by searching for a set of highly conserved, single-copy orthologs that are expected to be present in most species within a given lineage.

## Metrics
BUSCO categorizes the found orthologs into:
- **Complete and Single-copy (S)**: The gene is found exactly once and is complete.
- **Complete and Duplicated (D)**: The gene is found more than once and is complete.
- **Fragmented (F)**: Only a part of the gene is found.
- **Missing (M)**: The gene is not found.

The total completeness is calculated as $(S + D) / (S + D + F + M)$.

## Application in this Study
BUSCO (arthropoda_odb10) was used to evaluate the *Macrobrachium rosenbergii* transcriptome assembly, which achieved a completeness of 96.5%, indicating a high-quality assembly.

## Related Sources
- [[sources/U0001-0906202200531700.md]]