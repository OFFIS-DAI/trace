# one model per grid area, scenario and urbanization
codes_nan_filtered = [
    "1-MV-urban--1-no_sw",
    "1-LV-semiurb4--1-no_sw",
    "1-MVLV-rural-all-2-no_sw"
]

codes_nan = [
    "1-MV-rural–0-sw", "1-MV-rural–1-sw", "1-MV-rural–2-sw",
    "1-MV-semiurb–0-sw", "1-MV-semiurb–1-sw", "1-MV-semiurb–2-sw",
    "1-MV-urban–0-sw", "1-MV-urban–1-sw", "1-MV-urban–2-sw",
    "1-MV-comm–0-sw", "1-MV-comm–1-sw", "1-MV-comm–2-sw",

    "1-LV-rural1–0-sw", "1-LV-rural1–1-sw", "1-LV-rural1–2-sw",
    "1-LV-rural2–0-sw", "1-LV-rural2–1-sw", "1-LV-rural2–2-sw",
    "1-LV-rural3–0-sw", "1-LV-rural3–1-sw", "1-LV-rural3–2-sw",
    "1-LV-semiurb4–0-sw", "1-LV-semiurb4–1-sw", "1-LV-semiurb4–2-sw",
    "1-LV-semiurb5–0-sw", "1-LV-semiurb5–1-sw", "1-LV-semiurb5–2-sw",
    "1-LV-urban6–0-sw", "1-LV-urban6–1-sw", "1-LV-urban6–2-sw",

    "1-HVMV-mixed-all-0-sw", "1-HVMV-mixed-all-1-sw", "1-HVMV-mixed-all-2-sw",
    "1-HVMV-mixed-1.105-0-sw", "1-HVMV-mixed-1.105-1-sw", "1-HVMV-mixed-1.105-2-sw",
    "1-HVMV-mixed-2.102-0-sw", "1-HVMV-mixed-2.102-1-sw", "1-HVMV-mixed-2.102-2-sw",
    "1-HVMV-mixed-4.101-0-sw", "1-HVMV-mixed-4.101-1-sw", "1-HVMV-mixed-4.101-2-sw",
    "1-HVMV-urban-all-0-sw", "1-HVMV-urban-all-1-sw", "1-HVMV-urban-all-2-sw",
    "1-HVMV-urban-2.203-0-sw", "1-HVMV-urban-2.203-1-sw", "1-HVMV-urban-2.203-2-sw",
    "1-HVMV-urban-3.201-0-sw", "1-HVMV-urban-3.201-1-sw", "1-HVMV-urban-3.201-2-sw",
    "1-HVMV-urban-4.201-0-sw", "1-HVMV-urban-4.201-1-sw", "1-HVMV-urban-4.201-2-sw",

    "1-MVLV-rural-all-0-sw", "1-MVLV-rural-all-1-sw", "1-MVLV-rural-all-2-sw",
    "1-MVLV-rural-1.108-0-sw", "1-MVLV-rural-1.108-1-sw", "1-MVLV-rural-1.108-2-sw",
    "1-MVLV-rural-2.107-0-sw", "1-MVLV-rural-2.107-1-sw", "1-MVLV-rural-2.107-2-sw",
    "1-MVLV-rural-4.101-0-sw", "1-MVLV-rural-4.101-1-sw", "1-MVLV-rural-4.101-2-sw",
    "1-MVLV-semiurb-all-0-sw", "1-MVLV-semiurb-all-1-sw", "1-MVLV-semiurb-all-2-sw",
    "1-MVLV-semiurb-3.202-0-sw", "1-MVLV-semiurb-3.202-1-sw", "1-MVLV-semiurb-3.202-2-sw",
    "1-MVLV-semiurb-4.201-0-sw", "1-MVLV-semiurb-4.201-1-sw", "1-MVLV-semiurb-4.201-2-sw",
    "1-MVLV-semiurb-5.220-0-sw", "1-MVLV-semiurb-5.220-1-sw", "1-MVLV-semiurb-5.220-2-sw",
    "1-MVLV-urban-all-0-sw", "1-MVLV-urban-all-1-sw", "1-MVLV-urban-all-2-sw",
    "1-MVLV-urban-5.303-0-sw", "1-MVLV-urban-5.303-1-sw", "1-MVLV-urban-5.303-2-sw",
    "1-MVLV-urban-6.305-0-sw", "1-MVLV-urban-6.305-1-sw", "1-MVLV-urban-6.305-2-sw",
    "1-MVLV-urban-6.309-0-sw", "1-MVLV-urban-6.309-1-sw", "1-MVLV-urban-6.309-2-sw",
    "1-MVLV-comm-all-0-sw", "1-MVLV-comm-all-1-sw", "1-MVLV-comm-all-2-sw",
    "1-MVLV-comm-3.403-0-sw", "1-MVLV-comm-3.403-1-sw", "1-MVLV-comm-3.403-2-sw",
    "1-MVLV-comm-4.416-0-sw", "1-MVLV-comm-4.416-1-sw", "1-MVLV-comm-4.416-2-sw",
    "1-MVLV-comm-5.401-0-sw", "1-MVLV-comm-5.401-1-sw", "1-MVLV-comm-5.401-2-sw"
]

codes_wan_filtered = [
    "1-MV-urban--1-no_sw", "1-MV-rural--0-no_sw"
]

codes_wan = [
    "1-HV-mixed–0-sw", "1-HV-mixed–1-sw", "1-HV-mixed–2-sw",
    "1-HV-urban–0-sw", "1-HV-urban–1-sw", "1-HV-urban–2-sw",

    "1-HVMV-mixed-all-0-sw", "1-HVMV-mixed-all-1-sw", "1-HVMV-mixed-all-2-sw",
    "1-HVMV-mixed-1.105-0-sw", "1-HVMV-mixed-1.105-1-sw", "1-HVMV-mixed-1.105-2-sw",
    "1-HVMV-mixed-2.102-0-sw", "1-HVMV-mixed-2.102-1-sw", "1-HVMV-mixed-2.102-2-sw",
    "1-HVMV-mixed-4.101-0-sw", "1-HVMV-mixed-4.101-1-sw", "1-HVMV-mixed-4.101-2-sw",
    "1-HVMV-urban-all-0-sw", "1-HVMV-urban-all-1-sw", "1-HVMV-urban-all-2-sw",
    "1-HVMV-urban-2.203-0-sw", "1-HVMV-urban-2.203-1-sw", "1-HVMV-urban-2.203-2-sw",
    "1-HVMV-urban-3.201-0-sw", "1-HVMV-urban-3.201-1-sw", "1-HVMV-urban-3.201-2-sw",
    "1-HVMV-urban-4.201-0-sw", "1-HVMV-urban-4.201-1-sw", "1-HVMV-urban-4.201-2-sw"
]

simbench_codes_low_voltage = [
    '1-LV-rural1--0-no_sw',
    '1-LV-rural1--1-no_sw',
    '1-LV-rural1--2-no_sw',
    '1-LV-rural2--0-no_sw',
    '1-LV-rural2--1-no_sw',
    '1-LV-rural2--2-no_sw',
    '1-LV-rural3--0-no_sw',
    '1-LV-rural3--1-no_sw',
    '1-LV-rural3--2-no_sw',
    '1-LV-semiurb4--0-no_sw',
    '1-LV-semiurb4--1-no_sw',
    '1-LV-semiurb4--2-no_sw',
    '1-LV-semiurb5--0-no_sw',
    '1-LV-semiurb5--1-no_sw',
    '1-LV-semiurb5--2-no_sw',
    '1-LV-urban6--0-no_sw',
    '1-LV-urban6--1-no_sw',
    '1-LV-urban6--2-no_sw'
]

simbench_codes_medium_low_voltage = [
    '1-MVLV-rural-all-0-no_sw',
    '1-MVLV-rural-all-1-no_sw',
    '1-MVLV-rural-all-2-no_sw',
    '1-MVLV-rural-1.108-0-no_sw',
    '1-MVLV-rural-1.108-1-no_sw',
    '1-MVLV-rural-1.108-2-no_sw',
    '1-MVLV-rural-2.107-0-no_sw',
    '1-MVLV-rural-2.107-1-no_sw',
    '1-MVLV-rural-2.107-2-no_sw',
    '1-MVLV-rural-4.101-0-no_sw',
    '1-MVLV-rural-4.101-1-no_sw',
    '1-MVLV-rural-4.101-2-no_sw',
    '1-MVLV-semiurb-all-0-no_sw',
    '1-MVLV-semiurb-all-1-no_sw',
    '1-MVLV-semiurb-all-2-no_sw',
    '1-MVLV-semiurb-3.202-0-no_sw',
    '1-MVLV-semiurb-3.202-1-no_sw',
    '1-MVLV-semiurb-3.202-2-no_sw',
    '1-MVLV-semiurb-4.201-0-no_sw',
    '1-MVLV-semiurb-4.201-1-no_sw',
    '1-MVLV-semiurb-4.201-2-no_sw',
    '1-MVLV-semiurb-5.220-0-no_sw',
    '1-MVLV-semiurb-5.220-1-no_sw',
    '1-MVLV-semiurb-5.220-2-no_sw',
    '1-MVLV-urban-all-0-no_sw',
    '1-MVLV-urban-all-1-no_sw',
    '1-MVLV-urban-all-2-no_sw',
    '1-MVLV-urban-5.303-0-no_sw',
    '1-MVLV-urban-5.303-1-no_sw',
    '1-MVLV-urban-5.303-2-no_sw',
    '1-MVLV-urban-6.305-0-no_sw',
    '1-MVLV-urban-6.305-1-no_sw',
    '1-MVLV-urban-6.305-2-no_sw',
    '1-MVLV-urban-6.309-0-no_sw',
    '1-MVLV-urban-6.309-1-no_sw',
    '1-MVLV-urban-6.309-2-no_sw',
    '1-MVLV-comm-all-0-no_sw',
    '1-MVLV-comm-all-1-no_sw',
    '1-MVLV-comm-all-2-no_sw',
    '1-MVLV-comm-3.403-0-no_sw',
    '1-MVLV-comm-3.403-1-no_sw',
    '1-MVLV-comm-3.403-2-no_sw',
    '1-MVLV-comm-4.416-0-no_sw',
    '1-MVLV-comm-4.416-1-no_sw',
    '1-MVLV-comm-4.416-2-no_sw',
    '1-MVLV-comm-5.401-0-no_sw',
    '1-MVLV-comm-5.401-1-no_sw',
    '1-MVLV-comm-5.401-2-no_sw'
]
