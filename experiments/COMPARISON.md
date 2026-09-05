# Cross-example comparison — design exemplars (Phase C/D output)

## Fixed dimensions × four exemplars

| Dimension         | arena-tem/v1                | arena-tem-t/v1              | mazehard-hrm/v1                  | mazehard-hrm-rl/v1               |
| ----------------- | --------------------------- | --------------------------- | -------------------------------- | -------------------------------- |
| Task/model        | arena × tem                 | arena × tem-t (model swap)  | mazehard × hrm                   | mazehard × hrm-rl                |
| Input adaptation  | relational-seq (obs/action) | relational-seq (same task)  | raster-seq (S=P=900)             | raster-seq (S=P=900) + reset     |
| Output adaptation | observation-prediction      | observation-prediction      | raster-prediction (schema_slots) | raster-prediction (schema_slots) |
| Pipeline/steps    | 1 in + 1 out                | 1 in + 1 out                | 1 in + decoder + 1 out           | 1 in + decoder + 1 out + ctrl    |
| Objectives        | 1 (supervised CE)           | 1 (supervised CE)           | 2 (CE + ACT halting)             | 2 (CE + RL control)              |
| Controllers       | none                        | none                        | none (supervised halt)           | **reusable deliberation ctrl**   |
| Protocols         | supervised replay           | supervised replay           | supervised CE + halting          | hybrid: supervised + RL          |
| Resources         | arena corpus (dg/obsfield)  | arena corpus                | mazehard corpus (maze-nd)        | mazehard corpus (maze-nd)        |
| Evaluation        | A_obs^rev + 3 pathways      | revisit metrics + its split | exact-solution + token + any-opt | same + halt/value diagnostics    |
| CLI UX            | ref-by-name; binding hidden | identical                   | identical + show needs decoder   | identical; RL invisible          |
| Python UX         | resolve + train             | same                        | same                             | same, hides controller           |
| Variation point   | baseline                    | model substitutability      | raster + decoder + 2nd objective | controller + RL objective        |
