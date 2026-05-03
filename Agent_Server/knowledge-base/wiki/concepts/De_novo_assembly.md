# De novo assembly

**De novo assembly** is the process of reconstructing a genome or transcriptome from scratch without the use of a pre-existing reference sequence. This is particularly crucial for non-model organisms that do not have a high-quality reference genome available.

## Process
1. **Sequencing**: Generating short or long reads from DNA or RNA.
2. **Overlapping**: Finding overlapping sequences between reads.
3. **Contig Construction**: Merging overlapping reads into longer continuous sequences called **contigs**.
4. **Scaffolding**: Ordering and orienting contigs to form larger scaffolds.

## Challenges
- **Repetitive Sequences**: Highly repetitive regions can lead to assembly gaps or errors.
- **Computational Cost**: Requires significant memory and processing power.

## Application in this Study
The transcriptome of *Macrobrachium rosenbergii* was assembled *de novo* using the Trinity software, integrating multiple RNA-seq datasets to ensure comprehensive coverage of expressed genes.

## Related Sources
- [[sources/U0001-0906202200531700.md]]