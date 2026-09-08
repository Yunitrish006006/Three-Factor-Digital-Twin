# SHA-001 actual evidence
Status: completed unadopted extension. H-SHA-01 supported within hydronic selected-policy confirmation only; not supported as a universal cross-device improvement. No adopted thesis edits.

## Frozen execution
20 newdevelopment episodes plus12 uniqueconfirmation episodes=32 newFMU runs,348 scoredh+768 warmuph=1116 aggregate simulatedh.13 references:5 old same-configuration development baselines and8 same-date confirmation purePI fallbacks. Aggregate per-episode wall1482.489s (not elapsed task time, runs overlap). Newcandidate trials12h/device; including existingbaseline3h and2hidentification nominalexposure17h. Priorresearchsearchcosts remain extra. No lower total tuning cost demonstrated.

## Selection and confirmation
Only hydronic selected15_retain. Air,heat_pump,apartment,commercial selectedpurePI; fallbackexactreuse is preservation notimprovement.
Hydronic day48 earlyMAE0.959566631→0.744839139°C (22.37755% improvement),lateMAE0.300480590→0.245169911°C (18.40740%), acquisition560→499min (61min earlier). Day83 early0.964381804→0.748700046°C (22.36477%),late1.001275933→0.960231985°C (4.09916%), acquisition538→527min (11min earlier). Both dates allfrozengatesPASS. Day83 latepeak2.647303137°C remains, so this is not absolute precision control or all-day target maintenance.

## Factorial development findings
Verification contains4pairedcontrasts/device (20total),8scalarwindowmetrics/contrast, matchingexact JSON endpoint values. Same-duration modes have identical commanded inputs/temperatures before their handover; same-mode durations share identicalprefix until earlierhandover. AllprefixchecksPASS.
Hydronic day8:15_taper earlyMAE0.874886200,late0.707422067;15_retain0.729392304,0.455386220;55_taper0.748891381,0.703236216;55_retain0.747808810,0.503450778. At15min transferring remaining correction tointegral improves both windows over taper. At55min retain mostly improves laterwindow; longerperiod alone doesnotdominate shorterperiod when retainingstate. These are developmentFMU intervention contrasts, not real-device population estimates or independent new-datefactorial confirmation.15min is one of two testedtimes, not a measuredoptimalboundaryinterval. Transferredcorrection persists asintegralstate; externalcorrectionzero doesnotmean all earlierassistance influencevanishes.
Air15_retain improvesearlyMAE0.127459541→0.116469628 but acquisition16→18min violates+1min gate. Otherairpoliciesalsofail. Heatpump/commercial gains below1%; apartment fails earlycriterion. Preserve allnegativeandzero results.

## Verification
verify_boptest_handover.py PASS: fullsource/selection hashes, originalbaselineprovenance, alltrace hashes, everycommand/diagnostic replay, normalizedbounds, taper slew, integraltransfer mismatch<1e-10, irreversiblehandover, zeroexternalcorrection after60min, trajectorycontinuity, allmetrics/gates andfactorprefixidentity. FullPython suite274testsPASS in595.041s,including4new tests forordinaryPIidentity,factorprefix/handover,deadline/postPI,andbotherrorcrossings.
Offline report docs/reports/boptest_handover_2026-09-08_zh.html.3D phase-specificbaseline comparisons andfixedfactor comparisons derive fromcanonical JSON; syncverification separate.

## Scope and decision
Keep method as unadopted exploratorycontrol extension. KnownfiveFMUs, customFMPy runner with officialBOPTESTv0.9.0; noREST/KPI equivalence, unknownplantgenerality,hardware,RH,EUV,NN claim. Priorroundconfirmationdatesdiffer: do not directlyrank old/newmethods from their percentages. Nextresearch could refine durationnear15min whilepreservinghandovermode, with a newsharedbudget andunopenedconfirmationdata; notperformedhere.
